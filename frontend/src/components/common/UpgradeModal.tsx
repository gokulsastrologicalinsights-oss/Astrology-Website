"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { useAuth } from "@/lib/auth-context";
import { loadRazorpayScript } from "@/lib/razorpay";
import {
  Crown,
  Sparkles,
  CheckCircle2,
  Lock,
  X,
  ArrowRight,
  ShieldCheck,
  Zap,
  Loader2,
  CreditCard,
  FileText,
} from "lucide-react";

interface UpgradeModalProps {
  isOpen: boolean;
  onClose: () => void;
  toolNameEn?: string;
  toolNameTa?: string;
  requiredPlan?: "basic" | "tamil_specialist" | "pro";
}

export function UpgradeModal({
  isOpen,
  onClose,
  toolNameEn = "Premium Astrology Tool",
  toolNameTa = "கட்டண ஜோதிடக் கருவி",
  requiredPlan = "pro",
}: UpgradeModalProps) {
  const { language } = useLanguage();
  const { user, isAuthenticated, refreshUser } = useAuth();
  const router = useRouter();

  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const planTitleEn =
    requiredPlan === "tamil_specialist"
      ? "Tamil Horoscope Specialist"
      : requiredPlan === "basic"
      ? "Basic Astrologer"
      : "Pro Astrologer Studio";

  const planTitleTa =
    requiredPlan === "tamil_specialist"
      ? "தமிழ் ஜாதகப் பிரதியாளர் திட்டம்"
      : requiredPlan === "basic"
      ? "அடிப்படை ஜோதிடர் திட்டம்"
      : "முழு தொழில்முறை ஜோதிட மையம் (Pro)";

  const priceInr =
    requiredPlan === "tamil_specialist"
      ? 1999
      : requiredPlan === "basic"
      ? 999
      : 2999;

  // Single Report Unlock Price
  const singleReportPrice = 199;

  const handleCheckout = async (type: "subscription" | "single") => {
    if (!isAuthenticated || !user) {
      router.push(`/login?redirect=/tools`);
      return;
    }

    setIsProcessing(true);
    setErrorMessage(null);

    try {
      const isLoaded = await loadRazorpayScript();
      if (!isLoaded) {
        setErrorMessage(
          language === "ta"
            ? "Razorpay பணம் செலுத்தும் முறையை ஏற்ற முடியவில்லை. இணைய இணைப்பை சரிபார்க்கவும்."
            : "Could not load Razorpay payment gateway. Please check your internet connection."
        );
        setIsProcessing(false);
        return;
      }

      // Create Order
      const res = await fetch("/api/payments/create-order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          type === "single"
            ? { singleItemKey: "single_tool_unlock" }
            : { planId: requiredPlan, billingCycle: "monthly" }
        ),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        setErrorMessage(data.error || "Failed to initiate payment checkout.");
        setIsProcessing(false);
        return;
      }

      const options = {
        key: data.keyId,
        amount: data.amount,
        currency: data.currency,
        name: "Gokul's Astrological Insights",
        description: type === "single" ? `Instant Unlock: ${toolNameEn}` : `${data.planNameEn} (Monthly)`,
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
            const verifyRes = await fetch("/api/payments/verify", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
                planId: type === "single" ? "single_tool_unlock" : requiredPlan,
                billingCycle: type === "single" ? "one-time" : "monthly",
                isSingleService: type === "single",
              }),
            });

            const verifyData = await verifyRes.json();
            if (verifyRes.ok && verifyData.success) {
              await refreshUser();
              onClose();
              window.location.reload();
            } else {
              setErrorMessage(
                verifyData.error ||
                  "Payment verified with warning. Please contact support."
              );
            }
          } catch (err: any) {
            setErrorMessage("Error verifying payment completion: " + err.message);
          } finally {
            setIsProcessing(false);
          }
        },
        modal: {
          ondismiss: function () {
            setIsProcessing(false);
          },
        },
      };

      const rzpInstance = new (window as any).Razorpay(options);
      rzpInstance.open();
    } catch (err: any) {
      console.error(err);
      setErrorMessage(err?.message || "Failed to initiate payment gateway.");
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0A1626]/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg rounded-2xl bg-white shadow-2xl border border-[#D9DEE7] overflow-hidden">
        {/* Header Ribbon */}
        <div className="bg-gradient-to-r from-[#153F6B] via-[#1E4E82] to-[#153F6B] p-5 text-white relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1.5 rounded-full text-white/80 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-2 mb-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wider uppercase bg-[#FAF2DE] text-[#8B6914] border border-[#B4872B]/40">
              <Crown className="w-3.5 h-3.5" />
              {requiredPlan === "tamil_specialist"
                ? "TAMIL PRO"
                : requiredPlan === "basic"
                ? "BASIC"
                : "PRO ONLY"}
            </span>
            <span className="text-xs text-white/80">
              {language === "ta" ? "நேரடி ஆன்லைன் திறப்பு" : "Instant Online Access"}
            </span>
          </div>

          <h3 className="text-xl font-extrabold tracking-tight">
            {language === "ta" ? toolNameTa : toolNameEn}
          </h3>
          <p className="text-xs text-white/85 mt-1">
            {language === "ta"
              ? "இந்த உயர்ரக ஜோதிடக் கணக்கீட்டை உடனடியாகப் பெற ஒற்றைக் கட்டணம் அல்லது சந்தா திட்டத்தைத் தேர்ந்தெடுக்கவும்."
              : "Unlock this precision calculation engine instantly with Pay-Per-Report or Astrologer Subscription."}
          </p>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4">
          {errorMessage && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs">
              {errorMessage}
            </div>
          )}

          {/* Option A: Single Report Unlock (Retail Customer) */}
          <div className="rounded-xl bg-amber-50/80 border border-amber-300 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-amber-900 uppercase tracking-wider flex items-center gap-1.5">
                <FileText className="w-4 h-4 text-amber-600" />
                <span>{language === "ta" ? "ஒற்றை அறிக்கை கட்டணம் (வாடிக்கையாளர்)" : "Pay Per Report (Single Unlock)"}</span>
              </span>
              <span className="text-base font-black text-amber-900">
                ₹{singleReportPrice}
              </span>
            </div>
            <p className="text-xs text-amber-800">
              {language === "ta"
                ? "மாதாந்திர சந்தா தேவையில்லை. இந்த ஒரு ஜாதகம்/கருவிக்கு மட்டும் ₹199 செலுத்தி உடனடியாகப் பயன்படுத்தலாம்."
                : "No monthly subscription needed! Pay ₹199 once to calculate and export this report directly."}
            </p>
            <button
              onClick={() => handleCheckout("single")}
              disabled={isProcessing}
              className="w-full py-2.5 px-4 rounded-xl bg-amber-500 hover:bg-amber-600 text-slate-950 font-extrabold text-xs shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-70"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>{language === "ta" ? "திறக்கிறது..." : "Processing..."}</span>
                </>
              ) : (
                <>
                  <CreditCard className="w-4 h-4" />
                  <span>
                    {language === "ta"
                      ? `ஒற்றை அறிக்கைக்கு ₹${singleReportPrice} செலுத்துக (UPI / Card)`
                      : `Pay ₹${singleReportPrice} for Single Report (UPI / Card)`}
                  </span>
                </>
              )}
            </button>
          </div>

          <div className="relative flex py-1 items-center">
            <div className="flex-grow border-t border-slate-200"></div>
            <span className="flex-shrink mx-3 text-[11px] font-bold text-slate-600 uppercase">
              {language === "ta" ? "அல்லது மாதாந்திர சந்தா" : "Or Monthly Subscription"}
            </span>
            <div className="flex-grow border-t border-slate-200"></div>
          </div>

          {/* Option B: Astrologer Subscription */}
          <div className="rounded-xl bg-[#FAF2DE]/60 border border-[#B4872B]/30 p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[#8B6914] uppercase tracking-wider">
                {language === "ta" ? "முழு ஜோதிடர் திட்டம்" : "Astrologer Full Access"}
              </span>
              <span className="text-sm font-extrabold text-[#153F6B]">
                ₹{priceInr.toLocaleString()}/mo
              </span>
            </div>
            <h4 className="text-sm font-bold text-[#183047]">
              {language === "ta" ? planTitleTa : planTitleEn}
            </h4>
            <ul className="text-xs text-[#52667E] space-y-1 pt-1">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                <span>
                  {language === "ta"
                    ? "அளவற்ற ஜாதகங்கள் & 6-பக்க அச்சிடத்தக்க பிடிஎஃப்"
                    : "Unlimited calculations & high-res vector PDF booklets"}
                </span>
              </li>
            </ul>

            <button
              onClick={() => handleCheckout("subscription")}
              disabled={isProcessing}
              className="w-full mt-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-[#153F6B] to-[#1E4E82] hover:from-[#113255] hover:to-[#173F6B] text-white font-bold text-xs shadow-md transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-70"
            >
              <Zap className="w-4 h-4 text-amber-300" />
              <span>
                {language === "ta"
                  ? `சந்தா ஆக்டிவேட் செய்க: ₹${priceInr.toLocaleString()}/mo`
                  : `Subscribe Full Plan: ₹${priceInr.toLocaleString()}/mo`}
              </span>
            </button>
          </div>

          <div className="flex items-center justify-between pt-1">
            <Link
              href="/pricing"
              onClick={onClose}
              className="text-xs text-primary font-bold hover:underline flex items-center gap-1"
            >
              <span>{language === "ta" ? "அனைத்து கட்டண திட்டங்களையும் காண்க" : "Compare All Plans"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>

            <div className="flex items-center gap-1 text-[11px] text-slate-600">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              <span>Razorpay Verified</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
