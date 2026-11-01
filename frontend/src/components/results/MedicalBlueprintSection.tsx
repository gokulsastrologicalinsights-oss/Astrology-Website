"use client";

import React, { useMemo } from "react";
import {
  HoroscopeResponse,
  MedicalAstrologyResponse,
  DasaResponse,
  AnatomicalSystemMapping,
} from "@/lib/types";
import {
  ShieldCheck,
  ShieldAlert,
  HeartPulse,
  Sparkles,
  Flame,
  Wind,
  Droplet,
  Clock,
  Compass,
  CheckCircle2,
  Activity,
  Utensils,
  Bed,
  Leaf,
  Calendar,
  Zap,
} from "lucide-react";

interface MedicalBlueprintSectionProps {
  medicalData: MedicalAstrologyResponse;
  horoscope?: HoroscopeResponse | null;
  dasa?: DasaResponse | null;
  language: "en" | "ta";
}

export function MedicalBlueprintSection({
  medicalData,
  horoscope,
  dasa,
  language,
}: MedicalBlueprintSectionProps) {
  const isTa = language === "ta";
  const { vedic_analysis: vedic } = medicalData;
  const { birth_chart: birthChart, current_period: currentPeriod } = vedic;

  // ---------------------------------------------------------------------------
  // 1. AYURVEDIC TRIDOSHA EVALUATION (VATA / PITTA / KAPHA)
  // ---------------------------------------------------------------------------
  const doshaBalance = useMemo(() => {
    let vataScore = 20;
    let pittaScore = 20;
    let kaphaScore = 20;

    if (!horoscope) {
      return { vata: 33, pitta: 34, kapha: 33, primary: "Sama (Balanced)", primaryTa: "சம பிரகிருதி", leadingDosha: "Pitta" };
    }

    const ascSign = horoscope.ascendant?.sign_name || "";
    const moonSign = horoscope.planets?.find((p) => p.name === "Moon")?.sign_name || "";
    const sunSign = horoscope.planets?.find((p) => p.name === "Sun")?.sign_name || "";

    // Sign element classification
    const fireSigns = ["Aries", "Leo", "Sagittarius", "Mesha", "Simha", "Dhanus"];
    const earthSigns = ["Taurus", "Virgo", "Capricorn", "Rishaba", "Kanya", "Makara"];
    const airSigns = ["Gemini", "Libra", "Aquarius", "Mithuna", "Thula", "Kumbha"];
    const waterSigns = ["Cancer", "Scorpio", "Pisces", "Kataka", "Vrischika", "Meena"];

    const evalSign = (sign: string, weight: number) => {
      if (fireSigns.some((s) => sign.toLowerCase().includes(s.toLowerCase()))) {
        pittaScore += weight * 1.5;
      } else if (airSigns.some((s) => sign.toLowerCase().includes(s.toLowerCase()))) {
        vataScore += weight * 1.5;
      } else if (earthSigns.some((s) => sign.toLowerCase().includes(s.toLowerCase()))) {
        kaphaScore += weight;
        vataScore += weight * 0.5;
      } else if (waterSigns.some((s) => sign.toLowerCase().includes(s.toLowerCase()))) {
        kaphaScore += weight * 1.5;
      }
    };

    // Ascendant has highest physiological weight (40%)
    evalSign(ascSign, 40);
    // Moon has emotional/metabolic weight (30%)
    evalSign(moonSign, 30);
    // Sun has cellular vitality weight (20%)
    evalSign(sunSign, 20);

    // Planet rulership adjustments
    (horoscope.planets || []).forEach((p) => {
      if (p.house === 1 || p.house === 6) {
        if (["Mars", "Sun", "Ketu"].includes(p.name)) pittaScore += 15;
        if (["Saturn", "Rahu"].includes(p.name)) vataScore += 15;
        if (["Jupiter", "Venus", "Moon"].includes(p.name)) kaphaScore += 15;
      }
    });

    const total = vataScore + pittaScore + kaphaScore;
    const vataPct = Math.round((vataScore / total) * 100);
    const pittaPct = Math.round((pittaScore / total) * 100);
    const kaphaPct = 100 - (vataPct + pittaPct);

    // Determine primary & secondary constitution
    const sorted = [
      { name: "Vata", nameTa: "வாதம்", pct: vataPct },
      { name: "Pitta", nameTa: "பித்தம்", pct: pittaPct },
      { name: "Kapha", nameTa: "கபம்", pct: kaphaPct },
    ].sort((a, b) => b.pct - a.pct);

    const primary = `${sorted[0].name}-${sorted[1].name} Prakriti`;
    const primaryTa = `${sorted[0].nameTa}-${sorted[1].nameTa} பிரகிருதி`;

    return {
      vata: vataPct,
      pitta: pittaPct,
      kapha: kaphaPct,
      primary,
      primaryTa,
      leadingDosha: sorted[0].name,
    };
  }, [horoscope]);

  // ---------------------------------------------------------------------------
  // 2. VITALITY SHIELD & IMMUNITY SCORE (ARISHTA BHANGA)
  // ---------------------------------------------------------------------------
  const vitalityAnalysis = useMemo(() => {
    let score = 65; // baseline moderate vitality
    const mitigations: string[] = [];

    // Check Lagna Lord dignity
    const lagnaLord = birthChart.lagna_analysis.lord_dignity;
    if (["Exalted", "Own Sign"].includes(lagnaLord)) {
      score += 15;
      mitigations.push(
        isTa
          ? "லக்னாதிபதி ஆட்சி/உச்சம் பெற்று உடலமைப்பை வலுப்படுத்துகிறார்"
          : "Lagna Lord is exceptionally dignified (Own/Exalted), bolstering innate immunity"
      );
    } else if (["Debilitated", "Combust"].includes(lagnaLord)) {
      score -= 10;
    }

    // Check Classical Mitigations in birthChart
    if (birthChart.conflicting_indications && birthChart.conflicting_indications.length > 0) {
      birthChart.conflicting_indications.forEach((ind) => {
        score += 8;
        mitigations.push(ind);
      });
    }

    // Check Benefics in Kendras from Horoscope
    if (horoscope) {
      const beneficsInKendras = (horoscope.planets || []).filter(
        (p) => ["Jupiter", "Venus"].includes(p.name) && [1, 4, 7, 10].includes(p.house || 0)
      );
      if (beneficsInKendras.length > 0) {
        score += 10;
        const names = beneficsInKendras.map((p) => p.name).join(", ");
        mitigations.push(
          isTa
            ? `கேந்திர ஸ்தானங்களில் சுப கிரகங்கள் (${names}) நிலைபெற்று அரிஷ்ட பங்க பாதுகாப்பு அளிக்கின்றன`
            : `Benefic Grahas (${names}) in Kendras form a protective Arishta Bhanga longevity citadel`
        );
      }
    }

    // Clamp score safely between 48% and 96%
    const finalScore = Math.min(Math.max(score, 48), 96);

    let statusEn = "Balanced Constitutional Fortitude";
    let statusTa = "சமநிலையான உடல் வலிமை & பாதுகாப்பு";
    let statusColor = "text-emerald-700 bg-emerald-50 border-emerald-200";

    if (finalScore >= 80) {
      statusEn = "High Recuperative Force & Resilience (Robust Shield)";
      statusTa = "உயர்ந்த நோய் எதிர்ப்பு ஆற்றல் & விரைவான மீட்பு பலம்";
      statusColor = "text-teal-800 bg-teal-50 border-teal-300";
    } else if (finalScore < 60) {
      statusEn = "Sensitive Constitution - Prioritize Regular Rest";
      statusTa = "உணர்திறன் மிக்க உடலமைப்பு - சீரான ஓய்வு அவசியம்";
      statusColor = "text-amber-800 bg-amber-50 border-amber-200";
    }

    return {
      score: finalScore,
      statusEn,
      statusTa,
      statusColor,
      mitigations,
    };
  }, [birthChart, horoscope, isTa]);

  // ---------------------------------------------------------------------------
  // 3. ANATOMICAL SENSITIVITIES & PREVENTIVE NURTURING
  // ---------------------------------------------------------------------------
  const sensitivitySystems = useMemo(() => {
    const list: AnatomicalSystemMapping[] = birthChart.anatomical_mappings || [];
    const prioritized = list.filter((s: AnatomicalSystemMapping) => s.status === "Afflicted" || s.status === "Mitigated");
    const displayList = prioritized.length >= 2 ? prioritized.slice(0, 4) : list.slice(0, 3);

    const getRecommendations = (graha: string) => {
      const g = (graha || "").toLowerCase();
      if (g.includes("sun") || g.includes("சூரியன்")) {
        return {
          herbEn: "Arjuna bark, Tulsi, Cardamom",
          herbTa: "மருதம்பட்டை, துளசி, ஏலக்காய்",
          dietEn: "Pomegranate, soaked almonds, warm light soups",
          dietTa: "மாதுளை, ஊறவைத்த பாதாம், எளிய சூப்",
          habitEn: "Morning sunlight exposure (Surya Namaskar), brisk walking",
          habitTa: "காலை சூரிய ஒளி (சூரிய நமஸ்காரம்), சுறுசுறுப்பான நடைபயிற்சி",
        };
      }
      if (g.includes("moon") || g.includes("சந்திரன்")) {
        return {
          herbEn: "Brahmi, Shankhpushpi, Chamomile",
          herbTa: "வல்லாரை, சங்குபுஷ்பி, சீமை சாமந்தி",
          dietEn: "Fresh coconut water, warm spiced milk, seasonal melons",
          dietTa: "இளநீர், மசாலா பால், நீர்ச்சத்து நிறைந்த பழங்கள்",
          habitEn: "Sound 8-hour sleep routine, moonlit evening calm walks",
          habitTa: "முறையான 8 மணி நேர உறக்கம், மாலை நேர அமைதியான நடைபயிற்சி",
        };
      }
      if (g.includes("mars") || g.includes("செவ்வாய்")) {
        return {
          herbEn: "Amla, Coriander seed infusion, Shatavari",
          herbTa: "நெல்லிக்காய், கொத்தமல்லி விதை குடிநீர், சதாவரி",
          dietEn: "Cooling cucumbers, mint, avoiding excessive deep-fried chili",
          dietTa: "வெள்ளரிக்காய், புதினா, காரம் மற்றும் எண்ணெயில் பொரித்த உணவுகளை குறைத்தல்",
          habitEn: "Avoid skipping meals; channel excess heat through cool hydration",
          habitTa: "உணவை தவிர்க்காமல் உண்ணுதல்; உடற்சூட்டை தணிக்க நீர் அருந்துதல்",
        };
      }
      if (g.includes("mercury") || g.includes("புதன்")) {
        return {
          herbEn: "Triphala, Licorice (Athimadhuram), Fennel seeds",
          herbTa: "திரிபலா, அதிமதுரம், பெருஞ்சீரகம்",
          dietEn: "Cooked seasonal vegetables, moong dal khichdi, digestive teas",
          dietTa: "வேகவைத்த காய்கறிகள், பாசிப்பருப்பு கிச்சடி, சீரகத் தண்ணீர்",
          habitEn: "Mindful unhurried eating, digital curfew 1 hour before sleep",
          habitTa: "அவசரமின்றி அமைதியாக உணவு அருந்துதல், படுக்கும் முன் மொபைல் திரையை தவிர்த்தல்",
        };
      }
      if (g.includes("jupiter") || g.includes("குரு")) {
        return {
          herbEn: "Turmeric, Bhumiamalaki (Keezhanelli), Fenugreek",
          herbTa: "மஞ்சள், கீழாநெல்லி, வெந்தயம்",
          dietEn: "Moderate sugar/sweets, increase leafy greens, warm lemon water",
          dietTa: "இனிப்புகளை குறைத்து, கீரை வகைகள் மற்றும் எலுமிச்சை மிதமான நீர்",
          habitEn: "Regular liver detox support, avoiding excessive sedentary hours",
          habitTa: "கல்லீரல் ஆரோக்கியத்தில் கவனம், அதிக நேரம் ஒரே இடத்தில் அமர்வதை தவிர்த்தல்",
        };
      }
      if (g.includes("venus") || g.includes("சுக்கிரன்")) {
        return {
          herbEn: "Gokshura, Punarnava, Rose petal infusion",
          herbTa: "நெருஞ்சில், மூக்கிரட்டை, ரோஜா இதழ் தேநீர்",
          dietEn: "Abundant pure water, barley water, fresh berries",
          dietTa: "போதுமான அளவு சுத்தமான நீர், பார்லி நீர், நாவல் பழங்கள்",
          habitEn: "Kidney hydration pacing, balanced electrolyte levels",
          habitTa: "சிறுநீரக பாதுகாப்பு, சீரான நீர் மற்றும் தாது உப்புகள் உட்கொள்ளல்",
        };
      }
      return {
        herbEn: "Ashwagandha, Guggulu, Ginger infusion",
        herbTa: "அமுக்கரா (அஸ்வகந்தா), குக்குலு, சுக்கு குடிநீர்",
        dietEn: "Sesame oil, warm cooked whole grains, stewed fruits",
        dietTa: "நல்லெண்ணெய் பயன்பாடு, சூடான தானிய உணவுகள், வேகவைத்த பழங்கள்",
        habitEn: "Gentle joint mobility exercises, warm Abhyanga self-massage",
        habitTa: "எளிய மூட்டு பயிற்சிகள், மிதமான நல்லெண்ணெய் தேய்த்துக் குளித்தல்",
      };
    };

    return displayList.map((sys: AnatomicalSystemMapping) => {
      const rec = getRecommendations(sys.planetary_governance);
      return {
        ...sys,
        recommendation: rec,
      };
    });
  }, [birthChart.anatomical_mappings]);

  // ---------------------------------------------------------------------------
  // 4. ENERGY CYCLES & CURRENT DASHA VITALITY ASSESSMENT
  // ---------------------------------------------------------------------------
  const PLANET_NAMES_TA: Record<string, string> = {
    Sun: "சூரியன்",
    Moon: "சந்திரன்",
    Mars: "செவ்வாய்",
    Rahu: "ராகு",
    Jupiter: "குரு",
    Saturn: "சனி",
    Mercury: "புதன்",
    Ketu: "கேது",
    Venus: "சுக்கிரன்",
  };

  const currentDashaVitality = useMemo(() => {
    // 1. Prioritize real-time operating period from dasa.active_period (Today / Current Date)
    const active = dasa?.active_period;
    let md = active?.mahadasha || currentPeriod.mahadasha || "Unknown";
    let ad = active?.antardasha || currentPeriod.bhukti || null;
    let pd = active?.pratyantardasha || currentPeriod.antara || null;
    const targetDate = active?.target_date_iso || null;

    // 2. Initial Birth Dasa (at exact time of birth) for historical comparison
    const birthLord = dasa?.birth_dasa_lord || null;
    const birthBalance = dasa?.birth_balance_formatted || null;

    // Dynamic Tree Traversal if active_period is missing or defaulted to birth dasa
    if ((md === "Unknown" || !ad || ad === "Active Bhukti" || md === birthLord) && dasa?.dasa_tree && dasa.dasa_tree.length > 0) {
      const nowJd = Date.now() / 86400000 + 2440587.5;
      const liveMaha = dasa.dasa_tree.find((m) => m.start_jd <= nowJd && nowJd < m.end_jd);
      if (liveMaha) {
        md = liveMaha.lord;
        const sub = liveMaha.sub_periods || [];
        const liveBhukti = sub.find((b) => b.start_jd <= nowJd && nowJd < b.end_jd);
        if (liveBhukti) {
          ad = liveBhukti.lord;
          const andhar = liveBhukti.sub_periods || [];
          const liveAntara = andhar.find((a) => a.start_jd <= nowJd && nowJd < a.end_jd);
          if (liveAntara) {
            pd = liveAntara.lord;
          }
        }
      }
    }

    if (md === "Unknown") md = "Active Dasha";
    if (!ad) ad = md;

    const hasAfflictedRules = (currentPeriod.matching_rules || []).some(
      (r) => r.is_active && r.status === "Qualifying"
    );

    let periodTypeEn = "Active Rejuvenation & Vitality Phase";
    let periodTypeTa = "ஆற்றல் & உடல் மேம்பாட்டு காலம்";
    let periodColor = "text-teal-900 bg-teal-50 border-teal-200";
    let adviceEn = "Optimal cycle for physical fitness, muscle tone building, and progressive lifestyle upgrades.";
    let adviceTa = "உடற்பயிற்சி தொடங்கவும், உடலை வலுப்படுத்தவும், நல்வாழ்வு பழக்கங்களை மேம்படுத்தவும் உகந்த காலம்.";

    if (hasAfflictedRules) {
      periodTypeEn = "Protective Rest & Equilibrium Phase";
      periodTypeTa = "ஓய்வு & எச்சரிக்கையுடன் பராமரிக்கும் காலம்";
      periodColor = "text-amber-900 bg-amber-50 border-amber-300";
      adviceEn = "Prioritize sleep hygiene, avoid prolonged physical exhaustion, and schedule preventive wellness checkups.";
      adviceTa = "போதுமான தூக்கம், அதிக மன உளைச்சலை தவிர்த்தல் மற்றும் வருடாந்திர மருத்துவ பரிசோதனைகளுக்கு முக்கியத்துவம் அளிக்கவும்.";
    }

    return {
      md,
      ad,
      pd,
      targetDate,
      birthLord,
      birthBalance,
      periodTypeEn,
      periodTypeTa,
      periodColor,
      adviceEn,
      adviceTa,
      hasAfflictedRules,
    };
  }, [currentPeriod, dasa]);

  return (
    <div className="space-y-6">
      {/* ----------------------------------------------------------------- */}
      {/* HEADER: MEDICAL BLUEPRINT MANDATE & PHILOSOPHY                    */}
      {/* ----------------------------------------------------------------- */}
      <div className="bg-gradient-to-r from-[#153F6B] via-[#1E4D82] to-[#2B6CB0] text-white rounded-xl p-5 shadow-sm space-y-3">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center backdrop-blur-xs">
              <Activity className="w-5 h-5 text-amber-300" />
            </div>
            <div>
              <h2 className="font-serif text-lg font-bold text-white tracking-wide">
                {isTa ? "மருத்துவ ஜோதிட வரைபடம் (Medical Blueprint)" : "Medical Astrology Blueprint"}
              </h2>
              <p className="text-xs text-white/80">
                {isTa
                  ? "உடலமைப்பு பிரகிருதி, முக்கிய உறுப்பு உணர்திறன் மற்றும் நடப்பு தசா நல்வாழ்வு வழிகாட்டி"
                  : "Constitutional Prakriti, Anatomical Sensitivity, & Chrono-Vitality Architecture"}
              </p>
            </div>
          </div>
          <span className="text-[11px] font-medium bg-amber-400/20 text-amber-200 border border-amber-300/30 px-3 py-1 rounded-full">
            {isTa ? "தடுப்பு & நல்வாழ்வு மையம்" : "Preventive Wellness Engine"}
          </span>
        </div>

        {/* Concise Ethical Note */}
        <div className="bg-black/20 rounded-lg p-3 text-xs text-white/90 flex items-start gap-2 border border-white/10">
          <ShieldAlert className="w-4 h-4 text-amber-300 shrink-0 mt-0.5" />
          <p className="leading-relaxed">
            {isTa
              ? "இந்த வரைபடம் உடலின் இயற்கையான சுபாவம் (பிரகிருதி) மற்றும் ஆற்றல் சமநிலையை அறிய மட்டுமே. இது நோயறிதல் அல்ல; ஏதேனும் உடல்நலப் பிரச்சனைகளுக்கு தகுதியான மருத்துவரை அணுகவும்."
              : "This blueprint highlights innate constitutional tendencies and energy pacing for preventive wellness. It does not replace professional clinical diagnostic procedures."}
          </p>
        </div>
      </div>

      {/* ----------------------------------------------------------------- */}
      {/* 3-CARD BLUEPRINT GRID                                             */}
      {/* ----------------------------------------------------------------- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* =============================================================== */}
        {/* CARD 1: CONSTITUTIONAL BLUEPRINT & VITALITY SHIELD              */}
        {/* =============================================================== */}
        <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-5 flex flex-col justify-between">
          <div className="space-y-4">
            {/* Card Header */}
            <div className="flex items-center justify-between border-b border-[#F2F3F5] pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-700 flex items-center justify-center">
                  <HeartPulse className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-[#183047]">
                    {isTa ? "1. உடலமைப்பு & உயிர் ஆற்றல்" : "1. Constitution & Vitality"}
                  </h3>
                  <span className="text-[10px] text-[#8190A6]">
                    {isTa ? "ஆயுர்வேத திரிதோஷ சமநிலை" : "Ayurvedic Tridosha Equilibrium"}
                  </span>
                </div>
              </div>
              <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                {isTa ? doshaBalance.primaryTa : doshaBalance.primary}
              </span>
            </div>

            {/* Dosha Progress Bars */}
            <div className="space-y-3 bg-[#F8FAFC] p-3.5 rounded-xl border border-[#E2E8F0]">
              <span className="text-xs font-bold text-[#153F6B] block">
                {isTa ? "இயற்கை சுபாவ விகிதம் (Dosha Balance)" : "Constitutional Breakdown"}
              </span>

              {/* Vata */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="flex items-center gap-1.5 text-sky-800">
                    <Wind className="w-3.5 h-3.5 text-sky-600" />
                    <span>{isTa ? "வாதம் (Vata - வாயு / இயக்கம்)" : "Vata (Air/Movement)"}</span>
                  </span>
                  <span className="font-mono text-sky-900">{doshaBalance.vata}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-sky-100 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-sky-400 to-sky-600 rounded-full transition-all duration-500"
                    style={{ width: `${doshaBalance.vata}%` }}
                  />
                </div>
              </div>

              {/* Pitta */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="flex items-center gap-1.5 text-amber-800">
                    <Flame className="w-3.5 h-3.5 text-amber-600" />
                    <span>{isTa ? "பித்தம் (Pitta - அக்னி / செரிமானம்)" : "Pitta (Fire/Metabolism)"}</span>
                  </span>
                  <span className="font-mono text-amber-900">{doshaBalance.pitta}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-amber-100 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-amber-400 to-amber-600 rounded-full transition-all duration-500"
                    style={{ width: `${doshaBalance.pitta}%` }}
                  />
                </div>
              </div>

              {/* Kapha */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="flex items-center gap-1.5 text-teal-800">
                    <Droplet className="w-3.5 h-3.5 text-teal-600" />
                    <span>{isTa ? "கபம் (Kapha - நீர் / உறுதி)" : "Kapha (Water/Structure)"}</span>
                  </span>
                  <span className="font-mono text-teal-900">{doshaBalance.kapha}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-teal-100 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-teal-400 to-teal-600 rounded-full transition-all duration-500"
                    style={{ width: `${doshaBalance.kapha}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Vitality & Arishta Bhanga Shield Meter */}
            <div className="space-y-2 border border-[#E2E8F0] p-3.5 rounded-xl bg-white">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-[#183047] flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  <span>{isTa ? "உயிர் ஆற்றல் & கவச நிலை" : "Innate Vitality Shield"}</span>
                </span>
                <span className="font-mono font-bold text-sm text-emerald-700">
                  {vitalityAnalysis.score}/100
                </span>
              </div>

              <div className="w-full h-2.5 rounded-full bg-gray-100 overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-teal-500 to-emerald-600 rounded-full"
                  style={{ width: `${vitalityAnalysis.score}%` }}
                />
              </div>

              <div className={`p-2 rounded-lg border text-[11px] font-semibold ${vitalityAnalysis.statusColor}`}>
                {isTa ? vitalityAnalysis.statusTa : vitalityAnalysis.statusEn}
              </div>

              {/* Active Classical Mitigations */}
              {vitalityAnalysis.mitigations.length > 0 && (
                <div className="pt-2 text-[11px] text-[#52667E] space-y-1">
                  <span className="font-bold text-[#153F6B] block">
                    {isTa ? "அரிஷ்ட பங்க பாதுகாப்பு:" : "Protective Mitigations:"}
                  </span>
                  <ul className="list-disc pl-4 space-y-0.5">
                    {vitalityAnalysis.mitigations.slice(0, 2).map((m, i) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Practical Lifestyle Guideline */}
          <div className="bg-[#FAF2DE]/50 border border-[#B4872B]/30 rounded-xl p-3 text-xs text-[#5F4917] space-y-1">
            <span className="font-bold flex items-center gap-1 text-[#8C6D23]">
              <Sparkles className="w-3.5 h-3.5 text-[#B4872B]" />
              {isTa ? "பரிந்துரைக்கப்படும் தினசரி பழக்கம்" : "Circadian Lifestyle Alignment"}
            </span>
            <p className="text-[11px] leading-relaxed">
              {doshaBalance.leadingDosha === "Pitta"
                ? isTa
                  ? "உடற்சூட்டை தணிக்கும் குளிர்ச்சியான உணவுகள், முறையான நீர் அருந்துதல் மற்றும் மதிய வெயிலை தவிர்த்தல் நலம்."
                  : "Prioritize cooling foods, unhurried eating, and adequate hydration to avoid metabolic burnout."
                : doshaBalance.leadingDosha === "Vata"
                ? isTa
                  ? "மிதமான சூடான சத்தான உணவுகள், குறிப்பிட்ட நேரத்தில் உறங்குதல் மற்றும் வாத அமைதிக்கான நல்லெண்ணெய் குளியல் நலம்."
                  : "Nourish with warm grounding meals, steady sleep schedules, and soothing warm oil massages."
                : isTa
                ? "சுறுசுறுப்பான காலை உடற்பயிற்சி, இலகுவான சூடான காரசார மசாலாக்கள் மற்றும் பகல் தூக்கத்தை தவிர்த்தல் நலம்."
                : "Favor light warming spices, brisk morning cardio, and avoid heavy daytime naps."}
            </p>
          </div>
        </div>

        {/* =============================================================== */}
        {/* CARD 2: ORGAN & ANATOMICAL SYSTEM SENSITIVITIES                 */}
        {/* =============================================================== */}
        <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-5 flex flex-col justify-between">
          <div className="space-y-4">
            {/* Card Header */}
            <div className="flex items-center justify-between border-b border-[#F2F3F5] pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center">
                  <Compass className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-[#183047]">
                    {isTa ? "2. உடல் உறுப்பு உணர்திறன்" : "2. Anatomical Sensitivities"}
                  </h3>
                  <span className="text-[10px] text-[#8190A6]">
                    {isTa ? "முக்கிய கவனிப்பு பகுதிகள்" : "Nurturing Sensitive Systems"}
                  </span>
                </div>
              </div>
              <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-900">
                {isTa ? "தடுப்பு விழிப்புணர்வு" : "Preventive Focus"}
              </span>
            </div>

            {/* Sensitivities List */}
            <div className="space-y-3">
              {sensitivitySystems.map((sys, idx: number) => (
                <div
                  key={`sys-item-${idx}`}
                  className="rounded-xl border border-[#E2E8F0] p-3.5 bg-[#F8FAFC] space-y-2.5 transition-all hover:border-amber-300"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="space-y-0.5">
                      <span className="font-bold text-xs text-[#153F6B] block">
                        {isTa ? sys.system_name_ta : sys.system_name_en}
                      </span>
                      <span className="text-[10px] text-[#8190A6]">
                        {isTa ? "ஆதிக்க கிரகம்:" : "Governor:"}{" "}
                        <span className="font-semibold text-[#183047]">{sys.planetary_governance}</span> (
                        {sys.sign_governance})
                      </span>
                    </div>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase tracking-wider ${
                        sys.status === "Afflicted"
                          ? "bg-amber-100 text-amber-800 border border-amber-300"
                          : "bg-emerald-100 text-emerald-800 border border-emerald-200"
                      }`}
                    >
                      {sys.status}
                    </span>
                  </div>

                  <p className="text-[11px] text-[#52667E] leading-relaxed">
                    {isTa ? sys.organs_ta : sys.organs_en}
                  </p>

                  {/* Gentle Herbal & Kitchen Advice */}
                  <div className="bg-white rounded-lg p-2.5 border border-[#E2E8F0] text-[11px] space-y-1">
                    <div className="flex items-center gap-1.5 text-emerald-800 font-bold">
                      <Leaf className="w-3.5 h-3.5 text-emerald-600" />
                      <span>{isTa ? "இயற்கை மூலிகைகள் & ஆதரவு:" : "Herbal & Dietary Support:"}</span>
                    </div>
                    <p className="text-[#334155] font-medium">
                      {isTa ? sys.recommendation.herbTa : sys.recommendation.herbEn}
                    </p>
                    <p className="text-[#64748B] text-[10px]">
                      {isTa ? sys.recommendation.dietTa : sys.recommendation.dietEn}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Safety Notice Footer */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 text-xs text-blue-900 flex items-start gap-2">
            <CheckCircle2 className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
            <p className="text-[11px] leading-relaxed">
              {isTa
                ? "குறிப்பு: இது குறிப்பிட்ட நோய்க்கான சான்று அல்ல; உடலின் எந்த பகுதியை கவனமுடன் பராமரிக்க வேண்டும் என்பதற்கான வழிகாட்டல் மட்டுமே."
                : "Reminder: Astrological sensitivities represent constitutional stress tendencies, not clinical diagnoses. Maintain healthy routine checkups."}
            </p>
          </div>
        </div>

        {/* =============================================================== */}
        {/* CARD 3: ENERGY CYCLES & STRESS TIMING (DASHA VITALITY)          */}
        {/* =============================================================== */}
        <div className="bg-white rounded-xl border border-[#D9DEE7] p-5 shadow-2xs space-y-5 flex flex-col justify-between">
          <div className="space-y-4">
            {/* Card Header */}
            <div className="flex items-center justify-between border-b border-[#F2F3F5] pb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-indigo-50 text-indigo-700 flex items-center justify-center">
                  <Clock className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-[#183047]">
                    {isTa ? "3. தசா காலக்கோடு & ஆற்றல்" : "3. Energy Cycles & Timing"}
                  </h3>
                  <span className="text-[10px] text-[#8190A6]">
                    {isTa ? "நடப்பு தசா-புக்தி நல்வாழ்வு" : "Current Dasha-Bhukti Pacing"}
                  </span>
                </div>
              </div>
              <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-900">
                {isTa ? "கால சுழற்சி" : "Chrono-Pacing"}
              </span>
            </div>

            {/* Current Active Dasha Banner */}
            <div className="rounded-xl border border-[#E2E8F0] p-4 bg-[#F8FAFC] space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-semibold text-[#8190A6] block">
                    {isTa ? "இன்றைய நடப்பு தசா - புக்தி:" : "Current Active Dasha / Bhukti (Today):"}
                  </span>
                  <span className="text-[10px] text-emerald-700 font-semibold flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    {isTa ? "இன்று இயங்கும் நடப்பு தசா காலம்" : "Live Real-Time Operating Period"}
                  </span>
                </div>
                <div className="text-right">
                  <span className="font-bold text-xs text-[#153F6B] bg-white px-3 py-1.5 rounded-lg border border-[#E2E8F0] inline-block shadow-2xs">
                    {isTa
                      ? `${PLANET_NAMES_TA[currentDashaVitality.md] || currentDashaVitality.md} - ${PLANET_NAMES_TA[currentDashaVitality.ad] || currentDashaVitality.ad}${
                          currentDashaVitality.pd ? ` - ${PLANET_NAMES_TA[currentDashaVitality.pd] || currentDashaVitality.pd}` : ""
                        }`
                      : `${currentDashaVitality.md} - ${currentDashaVitality.ad}${
                          currentDashaVitality.pd ? ` - ${currentDashaVitality.pd}` : ""
                        }`}
                  </span>
                </div>
              </div>

              {/* Status Badge */}
              <div className={`p-3 rounded-lg border text-xs font-bold space-y-1 ${currentDashaVitality.periodColor}`}>
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  <span>{isTa ? currentDashaVitality.periodTypeTa : currentDashaVitality.periodTypeEn}</span>
                </div>
                <p className="text-[11px] font-normal leading-relaxed opacity-90">
                  {isTa ? currentDashaVitality.adviceTa : currentDashaVitality.adviceEn}
                </p>
              </div>

              {/* Explicit Comparison: Initial Birth Dasa vs Today's Live Dasa */}
              {currentDashaVitality.birthLord && (
                <div className="pt-2 border-t border-[#E2E8F0] flex items-center justify-between text-[11px] text-[#64748B]">
                  <span>
                    {isTa ? "பிறப்பின் போது இருந்த தசா:" : "Initial Birth Dasa:"}{" "}
                    <strong className="text-[#334155]">{isTa ? (PLANET_NAMES_TA[currentDashaVitality.birthLord] || currentDashaVitality.birthLord) : currentDashaVitality.birthLord}</strong>
                    {currentDashaVitality.birthBalance ? ` (${currentDashaVitality.birthBalance})` : ""}
                  </span>
                  <span className="text-[10px] bg-slate-200/80 text-slate-700 px-1.5 py-0.5 rounded font-mono">
                    {isTa ? "ஆரம்ப பிறப்பு தசா" : "Birth Dasa"}
                  </span>
                </div>
              )}
            </div>

            {/* 4-Point Wellness Checklist for this Period */}
            <div className="space-y-2 border border-[#E2E8F0] p-3.5 rounded-xl bg-white">
              <span className="font-bold text-xs text-[#153F6B] block">
                {isTa ? "நடப்பு காலத்திற்கான 4 நல்வாழ்வு விதிகள்" : "4-Point Wellness Checklist"}
              </span>

              <div className="space-y-2 text-[11px] text-[#52667E]">
                <div className="flex items-start gap-2">
                  <Bed className="w-3.5 h-3.5 text-indigo-600 shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-[#183047] block">{isTa ? "உறக்கம் & அமைதி:" : "Sleep & Rest:"}</strong>
                    <span>
                      {isTa
                        ? "இரவு 10:30 மணிக்குள் படுக்கைக்குச் சென்று 7-8 மணி நேர ஆழ்ந்த தூக்கத்தை உறுதி செய்யவும்."
                        : "Maintain regular sleep by 10:30 PM with 7-8 hours of uninterrupted deep rest."}
                    </span>
                  </div>
                </div>

                <div className="flex items-start gap-2">
                  <Utensils className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-[#183047] block">{isTa ? "உணவு முறை:" : "Nutritional Cadence:"}</strong>
                    <span>
                      {isTa
                        ? "செரிமான அக்னியைப் பாதுகாத்து, குறிப்பிட்ட நேர இடைவெளியில் எளிதில் செரிக்கும் உணவு உட்கொள்ளவும்."
                        : "Eat at consistent intervals to support enzymatic digestive fire (Agni)."}
                    </span>
                  </div>
                </div>

                <div className="flex items-start gap-2">
                  <Activity className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-[#183047] block">{isTa ? "உடற்பயிற்சி:" : "Movement Cadence:"}</strong>
                    <span>
                      {isTa
                        ? "அதிகப்படியான சோர்வை தவிர்த்து, யோகாசனம், பிராணாயாமம் மற்றும் மிதமான நடைபயிற்சி சிறந்தது."
                        : "Balance physical exertion with restorative yoga, gentle stretching, and mindful breathwork."}
                    </span>
                  </div>
                </div>

                <div className="flex items-start gap-2">
                  <Calendar className="w-3.5 h-3.5 text-teal-600 shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-[#183047] block">{isTa ? "தடுப்பு பரிசோதனை:" : "Preventive Screenings:"}</strong>
                    <span>
                      {isTa
                        ? "வழக்கமான ரத்த அழுத்த, ரத்த சர்க்கரை மற்றும் உடல்நலப் பரிசோதனைகளை காலத்தோடு செய்து கொள்ளவும்."
                        : "Schedule standard routine preventive health screenings during sensitive sub-periods."}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Calming Propitiation Note */}
          <div className="bg-[#FAF2DE]/50 border border-[#B4872B]/30 rounded-xl p-3 text-xs text-[#5F4917] flex items-center justify-between">
            <span className="font-semibold text-[11px]">
              {isTa ? "அமைதிக்கான தியானம்: தினமும் 15 நிமிடம் பிராணாயாமம்" : "Daily Restorative Habit: 15 mins Pranayama"}
            </span>
            <Sparkles className="w-4 h-4 text-[#B4872B]" />
          </div>
        </div>
      </div>
    </div>
  );
}
