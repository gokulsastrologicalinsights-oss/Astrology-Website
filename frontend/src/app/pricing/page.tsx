"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { loadRazorpayScript } from "@/lib/razorpay";
import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import {
  Crown,
  Sparkles,
  Check,
  X as CloseIcon,
  ShieldCheck,
  Zap,
  BookOpen,
  Layers,
  Heart,
  Calendar,
  Compass,
  Hash,
  Users,
  FileDown,
  ArrowRight,
  HelpCircle,
  Clock,
  Loader2,
  CheckCircle2,
} from "lucide-react";

export default function PricingPage() {
  const { language, t } = useLanguage();
  const { user, isAuthenticated, refreshUser } = useAuth();
  const router = useRouter();

  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly");
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const currentTier = user?.subscription?.tier || "free";
  const isSubActive = user?.subscription?.status === "active";

  const handleSubscribe = async (planId: "basic" | "tamil_specialist" | "pro") => {
    if (!isAuthenticated || !user) {
      router.push(`/login?redirect=/pricing`);
      return;
    }

    setLoadingPlan(planId);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const isLoaded = await loadRazorpayScript();
      if (!isLoaded) {
        setErrorMessage(
          language === "ta"
            ? "Razorpay பணம் செலுத்தும் முறையை ஏற்ற முடியவில்லை. தயவுசெய்து பக்கத்தை ரீப்ரெஷ் செய்து மீண்டும் முயற்சிக்கவும்."
            : "Could not load Razorpay payment gateway. Please check your internet connection."
        );
        setLoadingPlan(null);
        return;
      }

      // Step 1: Create Order on server
      const res = await fetch("/api/payments/create-order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          planId,
          billingCycle,
        }),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        setErrorMessage(data.error || "Failed to initiate payment checkout.");
        setLoadingPlan(null);
        return;
      }

      // Step 2: Open Razorpay Checkout modal
      const options = {
        key: data.keyId,
        amount: data.amount,
        currency: data.currency,
        name: "Gokul's Astrological Insights",
        description: `${data.planNameEn} (${billingCycle === "yearly" ? "Annual" : "Monthly"})`,
        image: "/favicon.ico",
        order_id: data.orderId,
        prefill: {
          name: data.user?.name || "",
          email: data.user?.email || "",
        },
        theme: {
          color: "#153F6B",
        },
        handler: async function (response: any) {
          try {
            // Step 3: Verify Signature on server
            const verifyRes = await fetch("/api/payments/verify", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
                planId,
                billingCycle,
              }),
            });

            const verifyData = await verifyRes.json();
            if (verifyRes.ok && verifyData.success) {
              setSuccessMessage(
                language === "ta"
                  ? `வாழ்த்துக்கள்! உங்கள் ${data.planNameTa} சந்தா வெற்றிகரமாக ஆக்டிவேட் செய்யப்பட்டது.`
                  : `Congratulations! Your ${data.planNameEn} subscription is now active.`
              );
              await refreshUser();
              setTimeout(() => {
                router.push("/tools");
              }, 2500);
            } else {
              setErrorMessage(
                verifyData.error ||
                  "Payment verified with warning. Please contact admin."
              );
            }
          } catch (err: any) {
            setErrorMessage("Error verifying payment completion: " + err.message);
          } finally {
            setLoadingPlan(null);
          }
        },
        modal: {
          ondismiss: function () {
            setLoadingPlan(null);
          },
        },
      };

      const razorpay = new window.Razorpay(options);
      razorpay.open();
    } catch (err: any) {
      setErrorMessage(err.message || "An unexpected error occurred.");
      setLoadingPlan(null);
    }
  };

  const plans = [
    {
      id: "basic" as const,
      nameEn: "Basic Astrologer",
      nameTa: "அடிப்படை ஜோதிடர் திட்டம்",
      badgeEn: "Starter",
      badgeTa: "துவக்க நிலை",
      monthlyPrice: 999,
      yearlyPrice: 9999,
      savingsTa: "ஆண்டுக்கு ₹1,989 சேமிப்பு",
      savingsEn: "Save ₹1,989 / year",
      descEn: "Essential Parashari calculations, Kundli matching, and daily Panchang for students and beginners.",
      descTa: "வேத ஜோதிடக் கணக்கீடுகள், திருமணப் பொருத்தம் மற்றும் பஞ்சாங்கம் அடங்கிய துவக்கத் திட்டம்.",
      features: [
        { en: "Parashari Vedic Charts (D1 Rasi & D9 Navamsha)", ta: "ராசி & நவாம்ச வேதச் சக்கரங்கள்", included: true },
        { en: "Shadbala & Ashtakavarga Balas", ta: "ஷட்பலம் & அஷ்டகவர்க்க கணக்கீடுகள்", included: true },
        { en: "Kundli Matching & 36 Ashta Kuta Guna Milan", ta: "திருமணப் பொருத்தம் & 36 குணங்கள்", included: true },
        { en: "Daily Panchangam & 24-Hora Advisor", ta: "தினசரி பஞ்சாங்கம் & 24-கிரக ஹோரை", included: true },
        { en: "Shastric Remedies & Navagraha Temples", ta: "நவகிரக பரிகாரங்கள் & ஸ்தல வழிகாட்டி", included: true },
        { en: "30 High-Resolution PDF Reports / Month", ta: "மாதம் 30 உயர்தர பிடிஎஃப் அறிக்கைகள்", included: true },
        { en: "Traditional Tamil 6-Page Booklet PDF", ta: "பாரம்பரிய 6-பக்க தமிழ் ஜாதக ஏடு", included: false },
        { en: "KP Astrology (249 Sub-Lords & Horary 1-249)", ta: "கே.பி. ஜோதிடம் & பிரசன்னம் 1-249", included: false },
        { en: "Master Prediction Suite & 1-5 Year Roadmap", ta: "மகா முழுமை கணிப்பு & வாழ்க்கை காலவரிசை", included: false },
        { en: "Astrologer CRM & Client Records", ta: "வாடிக்கையாளர் மேலாண்மை (CRM)", included: false },
      ],
      isPopular: false,
      accentColor: "border-slate-300",
      buttonBg: "bg-slate-800 hover:bg-slate-900 text-white",
    },
    {
      id: "tamil_specialist" as const,
      nameEn: "Tamil Horoscope Specialist",
      nameTa: "தமிழ் ஜாதகப் பிரதியாளர்",
      badgeEn: "Most Popular",
      badgeTa: "அதிகம் விரும்பப்படும் திட்டம்",
      monthlyPrice: 1999,
      yearlyPrice: 19999,
      savingsTa: "ஆண்டுக்கு ₹3,989 சேமிப்பு",
      savingsEn: "Save ₹3,989 / year",
      descEn: "Specialized for traditional Tamil astrologers writing 6-page horoscopes with Nazhigai math and Client CRM.",
      descTa: "தமிழ் வருட/மாத/நாழிகை வினாழிகையுடன் கூடிய பாரம்பரிய 6-பக்க ஜாதக ஏடு மற்றும் வாடிக்கையாளர் மேலாண்மை.",
      features: [
        { en: "Everything in Basic Plan", ta: "அடிப்படைத் திட்டத்தின் அனைத்து வசதிகளும்", included: true },
        { en: "Traditional 6-Page Tamil Booklet PDF Writing", ta: "பாரம்பரிய 6-பக்க தமிழ் ஜாதகப் புத்தகம் எழுதுதல்", included: true },
        { en: "Nazhigai & Vinazhigai Astronomical Offsets", ta: "நாழிகை, வினாழிகை துல்லியக் கணக்கீடு", included: true },
        { en: "Tamil Solar Calendar (Pangu, Matham, Thethi)", ta: "தமிழ் சூரிய நாட்காட்டி & தினசுத்தி", included: true },
        { en: "Archana Chit & Thiruvasagam Prayer Sheet", ta: "அர்ச்சனைச் சீட்டு & திருவாசக வழிபாட்டு ஏடு", included: true },
        { en: "Astrologer CRM Directory & Client History", ta: "வாடிக்கையாளர் விபரப் பதிவேடு (CRM)", included: true },
        { en: "Automated Birthday & Dasa Caution Alerts", ta: "பிறந்தநாள் & தசா-புத்தி எச்சரிக்கை அறிவிப்புகள்", included: true },
        { en: "100 Vector PDF Reports / Month", ta: "மாதம் 100 பிடிஎஃப் அச்சிடும் உரிமை", included: true },
        { en: "KP Astrology (249 Sub-Lords & Horary 1-249)", ta: "கே.பி. ஜோதிடம் & பிரசன்னம் 1-249", included: false },
        { en: "Chaldean & Pythagorean Numerology Studio", ta: "எண் கணித அரங்கம் & பெயர் திருத்தம்", included: false },
      ],
      isPopular: true,
      accentColor: "border-[#B4872B] ring-2 ring-[#B4872B]/50",
      buttonBg: "bg-gradient-to-r from-[#B4872B] to-[#8B6914] hover:from-[#9c7422] hover:to-[#745710] text-white shadow-md",
    },
    {
      id: "pro" as const,
      nameEn: "Pro / Commercial Studio",
      nameTa: "முழு தொழில்முறை ஜோதிட மையம்",
      badgeEn: "Ultimate All-in-One",
      badgeTa: "முழுமையான தீர்வு",
      monthlyPrice: 2999,
      yearlyPrice: 29999,
      savingsTa: "ஆண்டுக்கு ₹5,989 சேமிப்பு",
      savingsEn: "Save ₹5,989 / year",
      descEn: "Complete flagship workstation: KP 249, Horary 1-249, Master Prediction Suite, Numerology, and Unlimited PDFs.",
      descTa: "கே.பி 249, பிரசன்னம், மகா முழுமை கணிப்பு, எண் கணிதம், வாஸ்து மற்றும் அளவற்ற பிடிஎஃப் கொண்ட முழு மையம்.",
      features: [
        { en: "Everything in Tamil Specialist Plan", ta: "தமிழ் பிரதியாளர் திட்டத்தின் அனைத்து வசதிகளும்", included: true },
        { en: "Advanced KP System (249 Sub-Lords, Placidus Cusps)", ta: "உயர்நிலை கே.பி (249 உப-அதிபதிகள், பாவக ஆரம்பங்கள்)", included: true },
        { en: "KP Horary 1–249 & 110 Life Events Predictor", ta: "1–249 பிரசன்ன கணிப்பான் & 110 நிகழ்வு ஆய்வுகள்", included: true },
        { en: "Master Prediction Suite (All-In-One Unified Life Roadmap)", ta: "மகா முழுமை கணிப்பு (ஒரே திரையில் அனைத்து ஆய்வுகள்)", included: true },
        { en: "Jamakkol Prasanam Horary (16-Jamam Dual-Ring Chart)", ta: "ஜாமக்கோள் பிரசன்னம் (16-ஜாம சக்கரம் & காரிய சித்தி)", included: true },
        { en: "Pancha Pakshi Shastra (Sage Agastya 5-Bird Rhythms)", ta: "அகத்தியர் பஞ்ச பட்சி சாஸ்திரம் (அரசு, ஊண் அந்தர காலங்கள்)", included: true },
        { en: "Numerology Studio (Chaldean, Pythagorean, Lo Shu)", ta: "எண் கணித அரங்கம் & வண்டி/மொபைல் எண் பொருத்தம்", included: true },
        { en: "Instant Customer Revelation Teleprompter", ta: "வாடிக்கையாளர் நேரடி வாக்கு பலகை (உடனடி பலன்)", included: true },
        { en: "Unlimited Vector PDF Reports & Printing Rights", ta: "அளவற்ற பிடிஎஃப் & அச்சிடும் முழு வணிக உரிமை", included: true },
        { en: "Commercial Astrology Practice License", ta: "தொழில்முறை ஜோதிட வணிகப் பயன்பாட்டு உரிமம்", included: true },
      ],
      isPopular: false,
      accentColor: "border-[#153F6B] ring-2 ring-[#153F6B]/30",
      buttonBg: "bg-gradient-to-r from-[#153F6B] to-[#1E4E82] hover:from-[#113255] hover:to-[#173F6B] text-white shadow-md",
    },
  ];

  return (
    <div className="min-h-screen bg-[#F2F3F5] text-[#183047]">
      {/* Top Banner */}
      <div className="bg-gradient-to-b from-[#153F6B] to-[#1E4E82] text-white pt-8 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto space-y-4">
          <Breadcrumbs
            items={[
              { label: language === "ta" ? "முகப்பு" : "Home", href: "/" },
              { label: language === "ta" ? "கட்டண சேவைகள் & திட்டங்கள்" : "Pricing & Plans" },
            ]}
          />

          <div className="text-center max-w-3xl mx-auto space-y-3 pt-4">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-400/20 border border-amber-300/30 text-amber-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5" />
              <span>
                {language === "ta"
                  ? "தொழில்முறை ஜோதிட மென்பொருள் சந்தா"
                  : "Professional Astrology Software Workstation"}
              </span>
            </div>
            <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
              {language === "ta"
                ? "உங்கள் ஜோதிடப் பயிற்சிக்கான கட்டணத் திட்டங்கள்"
                : "Simple, Transparent Plans for Every Astrologer"}
            </h1>
            <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
              {language === "ta"
                ? "முழுமையான வேத, கே.பி, பாரம்பரிய தமிழ் ஜாதகம் மற்றும் பிரசன்னக் கருவிகளை வரம்பற்ற அணுகலில் பெறுங்கள்."
                : "Unlock full Parashari, Advanced KP 249, Traditional Tamil Booklets, and Jamakkol Horary powered by high-precision astronomical calculations."}
            </p>

            {/* Billing Cycle Switcher */}
            <div className="pt-4 flex items-center justify-center">
              <div className="bg-white/10 p-1 rounded-full border border-white/20 inline-flex items-center shadow-inner">
                <button
                  type="button"
                  onClick={() => setBillingCycle("monthly")}
                  className={`px-5 py-2 rounded-full text-xs font-bold transition-all ${
                    billingCycle === "monthly"
                      ? "bg-white text-[#153F6B] shadow-sm"
                      : "text-white/80 hover:text-white"
                  }`}
                >
                  {language === "ta" ? "மாதாந்திர சந்தா" : "Monthly Billing"}
                </button>
                <button
                  type="button"
                  onClick={() => setBillingCycle("yearly")}
                  className={`px-5 py-2 rounded-full text-xs font-bold transition-all flex items-center gap-1.5 ${
                    billingCycle === "yearly"
                      ? "bg-amber-400 text-stone-900 shadow-sm"
                      : "text-white/80 hover:text-white"
                  }`}
                >
                  <span>{language === "ta" ? "ஆண்டுச் சந்தா" : "Annual Billing"}</span>
                  <span className="px-1.5 py-0.5 rounded-full text-[10px] bg-red-600 text-white font-extrabold animate-pulse">
                    {language === "ta" ? "2 மாதம் இலவசம்" : "Save 17%"}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Pricing Cards Container */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 pb-16 space-y-12">
        {/* Messages */}
        {errorMessage && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm flex items-center gap-2 shadow-sm">
            <CloseIcon className="w-5 h-5 shrink-0 text-red-600" />
            <span>{errorMessage}</span>
          </div>
        )}

        {successMessage && (
          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-300 text-emerald-800 text-sm flex items-center gap-2 shadow-sm">
            <CheckCircle2 className="w-5 h-5 shrink-0 text-emerald-600" />
            <span>{successMessage}</span>
          </div>
        )}

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8 items-stretch">
          {plans.map((plan) => {
            const isCurrent = isSubActive && currentTier === plan.id;
            const price = billingCycle === "yearly" ? plan.yearlyPrice : plan.monthlyPrice;
            const isLoading = loadingPlan === plan.id;

            return (
              <div
                key={plan.id}
                className={`relative rounded-3xl bg-white border ${plan.accentColor} shadow-md hover:shadow-xl transition-all duration-300 flex flex-col p-6 sm:p-7 ${
                  plan.isPopular ? "scale-[1.02] shadow-xl border-[#B4872B]" : ""
                }`}
              >
                {/* Popular / Recommended Tag */}
                {plan.isPopular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-[#B4872B] to-[#8B6914] text-white text-[11px] font-bold tracking-wider uppercase shadow-md flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-amber-300" />
                    <span>{language === "ta" ? plan.badgeTa : plan.badgeEn}</span>
                  </div>
                )}

                {!plan.isPopular && (
                  <div className="mb-2">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide bg-slate-100 text-slate-700">
                      {language === "ta" ? plan.badgeTa : plan.badgeEn}
                    </span>
                  </div>
                )}

                <div className="space-y-2 mb-4">
                  <h3 className="text-lg sm:text-xl font-bold text-[#183047]">
                    {language === "ta" ? plan.nameTa : plan.nameEn}
                  </h3>
                  <p className="text-xs text-[#52667E] min-h-[36px] leading-relaxed">
                    {language === "ta" ? plan.descTa : plan.descEn}
                  </p>
                </div>

                {/* Price Display */}
                <div className="py-4 border-y border-slate-100 mb-6 space-y-1">
                  <div className="flex items-baseline gap-1">
                    <span className="text-3xl sm:text-4xl font-black text-[#153F6B]">
                      ₹{price.toLocaleString()}
                    </span>
                    <span className="text-xs font-semibold text-[#8190A6]">
                      /{billingCycle === "yearly" ? (language === "ta" ? "வருடம்" : "year") : (language === "ta" ? "மாதம்" : "month")}
                    </span>
                  </div>
                  {billingCycle === "yearly" && (
                    <div className="text-[11px] font-semibold text-emerald-700">
                      {language === "ta" ? plan.savingsTa : plan.savingsEn}
                    </div>
                  )}
                </div>

                {/* Features List */}
                <div className="space-y-3 flex-1 mb-8">
                  <div className="text-xs font-bold uppercase tracking-wider text-[#8190A6]">
                    {language === "ta" ? "அடங்கியுள்ள அம்சங்கள்:" : "What's Included:"}
                  </div>
                  <ul className="space-y-2.5 text-xs text-[#183047]">
                    {plan.features.map((feat, idx) => (
                      <li key={idx} className="flex items-start gap-2.5">
                        {feat.included ? (
                          <Check className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                        ) : (
                          <CloseIcon className="w-4 h-4 text-slate-300 shrink-0 mt-0.5" />
                        )}
                        <span
                          className={feat.included ? "font-medium" : "text-slate-400 line-through"}
                        >
                          {language === "ta" ? feat.ta : feat.en}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Call-to-Action Button */}
                <div className="pt-2">
                  <button
                    type="button"
                    onClick={() => handleSubscribe(plan.id)}
                    disabled={isLoading || isCurrent}
                    className={`w-full py-3.5 px-4 rounded-xl font-bold text-xs sm:text-sm tracking-wide transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-70 ${
                      isCurrent
                        ? "bg-emerald-600 text-white cursor-default"
                        : plan.buttonBg
                    }`}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>
                          {language === "ta" ? "திரை திறக்கிறது..." : "Opening Checkout..."}
                        </span>
                      </>
                    ) : isCurrent ? (
                      <>
                        <CheckCircle2 className="w-4 h-4" />
                        <span>{language === "ta" ? "தற்போதைய திட்டம் (Active)" : "Current Active Plan"}</span>
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4 text-amber-300" />
                        <span>
                          {language === "ta"
                            ? `இப்போதே துவங்க (₹${price.toLocaleString()})`
                            : `Subscribe Now (₹${price.toLocaleString()})`}
                        </span>
                      </>
                    )}
                  </button>
                  <div className="text-center text-[10px] text-[#8190A6] mt-2">
                    {language === "ta"
                      ? "UPI (GPay/PhonePe), Card & NetBanking உடனடி ஆக்டிவேஷன்"
                      : "Instant automated activation via UPI, GPay, PhonePe, Cards"}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Feature Comparison Matrix */}
        <div className="rounded-3xl bg-white border border-[#D9DEE7] p-6 sm:p-8 shadow-sm space-y-6">
          <div className="text-center max-w-xl mx-auto space-y-2">
            <h2 className="text-xl sm:text-2xl font-bold text-[#183047]">
              {language === "ta" ? "கருவிகள் மற்றும் அம்சங்களின் ஒப்பீடு" : "Detailed Tool & Feature Matrix"}
            </h2>
            <p className="text-xs text-[#52667E]">
              {language === "ta"
                ? "எந்தெந்த திட்டத்தில் எந்த மென்பொருள் கருவிகள் கிடைக்கின்றன என்பதை விரிவாக அறியுங்கள்."
                : "Compare every tool and algorithmic module across our subscription tiers."}
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-[#D9DEE7] text-[#153F6B] font-bold">
                  <th className="py-3 px-4">
                    {language === "ta" ? "ஜோதிட சேவை / தொகுதி" : "Astrology Service / Module"}
                  </th>
                  <th className="py-3 px-4 text-center">Basic (₹999)</th>
                  <th className="py-3 px-4 text-center text-[#B4872B]">
                    Tamil Specialist (₹1,999)
                  </th>
                  <th className="py-3 px-4 text-center text-[#153F6B]">Pro Studio (₹2,999)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#D9DEE7]">
                <tr>
                  <td className="py-3 px-4 font-semibold text-[#183047]">
                    {language === "ta" ? "வேத ஜாதகம் (ராசி D1, நவாம்சம் D9 & வர்க்கங்கள்)" : "Parashari Vedic Charts & Vargas"}
                  </td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 font-semibold text-[#183047]">
                    {language === "ta" ? "திருமணப் பொருத்தம் & 36 குண மிலான்" : "Marriage Compatibility & 36 Ashta Kuta"}
                  </td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 font-semibold text-[#183047]">
                    {language === "ta" ? "தினசரி பஞ்சாங்கம் & 24 கிரக ஹோரை" : "Daily Panchangam & 24 Planetary Horas"}
                  </td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                </tr>
                <tr className="bg-amber-50/40">
                  <td className="py-3 px-4 font-semibold text-[#8B6914]">
                    {language === "ta" ? "பாரம்பரிய 6-பக்க தமிழ் ஜாதக ஏடு (PDF Booklet)" : "Traditional Tamil 6-Page Booklet PDF"}
                  </td>
                  <td className="py-3 px-4 text-center text-slate-300 font-bold">—</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                </tr>
                <tr className="bg-amber-50/40">
                  <td className="py-3 px-4 font-semibold text-[#8B6914]">
                    {language === "ta" ? "நாழிகை வினாழிகை & தமிழ் சூரிய காலண்டர்" : "Nazhigai/Vinazhigai & Tamil Solar Calendar"}
                  </td>
                  <td className="py-3 px-4 text-center text-slate-300 font-bold">—</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                </tr>
                <tr className="bg-amber-50/40">
                  <td className="py-3 px-4 font-semibold text-[#8B6914]">
                    {language === "ta" ? "ஜோதிடர் CRM & வாடிக்கையாளர் விபரங்கள்" : "Astrologer CRM & Client Directory"}
                  </td>
                  <td className="py-3 px-4 text-center text-slate-300 font-bold">—</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                </tr>
                <tr className="bg-blue-50/40">
                  <td className="py-3 px-4 font-semibold text-[#153F6B]">
                    {language === "ta" ? "உயர்நிலை கே.பி. அமைப்பு (249 உப-அதிபதிகள் & Placidus)" : "Advanced KP System (249 Sub-Lords)"}
                  </td>
                  <td className="py-3 px-4 text-center text-slate-300 font-bold">—</td>
                  <td className="py-3 px-4 text-center text-slate-300 font-bold">—</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                </tr>
                <tr className="bg-blue-50/40">
                  <td className="py-3 px-4 font-semibold text-[#153F6B]">
                    {language === "ta" ? "1–249 கே.பி. பிரசன்னம் & 110 நிகழ்வு கணிப்பான்" : "KP Horary 1-249 & 110 Events Predictor"}
                  </td>
                  <td className="py-3 px-4 text-center text-slate-300 font-bold">—</td>
                  <td className="py-3 px-4 text-center text-slate-300 font-bold">—</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                </tr>
                <tr className="bg-blue-50/40">
                  <td className="py-3 px-4 font-semibold text-[#153F6B]">
                    {language === "ta" ? "மகா முழுமை கணிப்பு (Master Prediction Suite)" : "Master Prediction Suite (All-In-One Roadmap)"}
                  </td>
                  <td className="py-3 px-4 text-center text-slate-300 font-bold">—</td>
                  <td className="py-3 px-4 text-center text-slate-300 font-bold">—</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                </tr>
                <tr className="bg-blue-50/40">
                  <td className="py-3 px-4 font-semibold text-[#153F6B]">
                    {language === "ta" ? "ஜாமக்கோள் பிரசன்னம் (16-ஜாம சக்கரம்)" : "Jamakkol Prasanam (16-Jamam Horary)"}
                  </td>
                  <td className="py-3 px-4 text-center text-slate-300 font-bold">—</td>
                  <td className="py-3 px-4 text-center text-slate-300 font-bold">—</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                </tr>
                <tr className="bg-blue-50/40">
                  <td className="py-3 px-4 font-semibold text-[#153F6B]">
                    {language === "ta" ? "பஞ்ச பட்சி சாஸ்திரம் & எண் கணித அரங்கம்" : "Pancha Pakshi & Numerology Studio"}
                  </td>
                  <td className="py-3 px-4 text-center text-slate-300 font-bold">—</td>
                  <td className="py-3 px-4 text-center text-slate-300 font-bold">—</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">✓</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 font-semibold text-[#183047]">
                    {language === "ta" ? "மாதாந்திர பிடிஎஃப் அறிக்கை உச்ச வரம்பு" : "Monthly PDF Export Quota"}
                  </td>
                  <td className="py-3 px-4 text-center font-bold">30</td>
                  <td className="py-3 px-4 text-center font-bold text-[#B4872B]">100</td>
                  <td className="py-3 px-4 text-center font-bold text-[#153F6B]">
                    {language === "ta" ? "வரம்பற்றது" : "Unlimited"}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Shastric Ephemeris & Security Trust Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-5 rounded-2xl bg-white border border-[#D9DEE7] flex items-start gap-3.5 shadow-2xs">
            <ShieldCheck className="w-6 h-6 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-bold text-[#183047]">
                {language === "ta" ? "துல்லிய வானியல் கணிதம்" : "Deterministic Precision"}
              </h4>
              <p className="text-xs text-[#52667E] mt-1 leading-relaxed">
                {language === "ta"
                  ? "உயர் துல்லிய வானியல் சூத்திரங்கள் மூலம் வினாடித் துல்லியத்தில் கிரக நிலைகள் கணக்கிடப்படுகின்றன."
                  : "All planetary positions and sub-lords calculate directly via high-precision astronomical algorithms."}
              </p>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-[#D9DEE7] flex items-start gap-3.5 shadow-2xs">
            <Zap className="w-6 h-6 text-amber-500 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-bold text-[#183047]">
                {language === "ta" ? "உடனடி தானியங்கி ஆக்டிவேஷன்" : "Instant Activation"}
              </h4>
              <p className="text-xs text-[#52667E] mt-1 leading-relaxed">
                {language === "ta"
                  ? "Razorpay மூலம் பணம் செலுத்திய உடனே உங்கள் கணக்கு தானாகவே பிரீமியம் நிலைக்கு மாறும்."
                  : "Your subscription activates automatically the second your UPI or card payment clears."}
              </p>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-white border border-[#D9DEE7] flex items-start gap-3.5 shadow-2xs">
            <Crown className="w-6 h-6 text-[#153F6B] shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-bold text-[#183047]">
                {language === "ta" ? "முழு வணிகப் பயன்பாட்டு உரிமை" : "Commercial Printing Rights"}
              </h4>
              <p className="text-xs text-[#52667E] mt-1 leading-relaxed">
                {language === "ta"
                  ? "உங்கள் பெயரில் அச்சிட்டு வாடிக்கையாளர்களுக்கு வழங்க முழு வணிக உரிமமும் வழங்கப்படுகிறது."
                  : "Print vector booklets and comprehensive reports branded for your professional clientele."}
              </p>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="rounded-3xl bg-white border border-[#D9DEE7] p-6 sm:p-8 shadow-sm space-y-6">
          <div className="flex items-center gap-2">
            <HelpCircle className="w-5 h-5 text-[#B4872B]" />
            <h3 className="text-lg sm:text-xl font-bold text-[#183047]">
              {language === "ta" ? "அடிக்கடி கேட்கப்படும் கேள்விகள் (FAQ)" : "Frequently Asked Questions"}
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
              <h4 className="font-bold text-[#183047]">
                {language === "ta"
                  ? "எந்தெந்த முறைகளில் பணம் செலுத்தலாம்?"
                  : "Which payment methods are accepted?"}
              </h4>
              <p className="text-[#52667E] leading-relaxed">
                {language === "ta"
                  ? "Razorpay மூலம் Google Pay, PhonePe, Paytm, BHIM UPI, மற்றும் அனைத்து கிரெடிட்/டெபிட் கார்டுகள் மற்றும் நெட் பேங்கிங் மூலம் உடனடியாகச் செலுத்தலாம்."
                  : "We accept all UPI apps (Google Pay, PhonePe, Paytm, BHIM), Indian & International Credit/Debit Cards, and NetBanking through Razorpay."}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
              <h4 className="font-bold text-[#183047]">
                {language === "ta"
                  ? "சந்தா முடிந்ததும் தானாக பணம் பிடிக்கப்படுமா?"
                  : "Will my card be charged automatically?"}
              </h4>
              <p className="text-[#52667E] leading-relaxed">
                {language === "ta"
                  ? "இல்லை. உங்கள் அனுமதி இன்றி தானாகப் பணம் பிடிக்கப்படாது. சந்தா காலம் முடியும் போது எளிதாக நீட்டித்துக் கொள்ளலாம்."
                  : "No automatic deductions take place without your explicit renewal. You can renew whenever your validity ends."}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
              <h4 className="font-bold text-[#183047]">
                {language === "ta"
                  ? "தமிழ் ஜாதகப் புத்தகம் அச்சிட எது சிறந்த திட்டம்?"
                  : "Which plan is best for traditional Tamil horoscope booklets?"}
              </h4>
              <p className="text-[#52667E] leading-relaxed">
                {language === "ta"
                  ? "தமிழ் ஜாதகப் பிரதியாளர் (₹1,999/மாதம்) அல்லது புரோ ஸ்டுடியோ திட்டம் தேர்ந்தெடுக்கவும். இதில் 6-பக்க ஏடு, தினசுத்தி, நாழிகை கணக்கு அத்தனையும் வரும்."
                  : "The Tamil Horoscope Specialist (₹1,999/mo) or Pro Studio plan includes the full 6-page booklet with Nazhigai and Archana slip."}
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
              <h4 className="font-bold text-[#183047]">
                {language === "ta"
                  ? "உதவி மற்றும் ஆலோசனை எங்கே தொடர்பு கொள்ள வேண்டும்?"
                  : "Where can I get customer assistance?"}
              </h4>
              <p className="text-[#52667E] leading-relaxed">
                {language === "ta"
                  ? "எங்கள் தொடர்புப் பக்கத்தின் (Contact Us) மூலமாகவோ அல்லது வாட்ஸ்அப் / மின்னஞ்சல் மூலமாகவோ நேரடியாக உதவி பெறலாம்."
                  : "Reach out anytime via our Contact Us page, email, or WhatsApp helpline for immediate support."}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
