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

  const handleQuickCheckout = async () => {
    if (!isAuthenticated || !user) {
      router.push(`/login?redirect=/pricing`);
      return;
    }

    setIsProcessing(true);
    setErrorMessage(null);

    try {
      const isLoaded = await loadRazorpayScript();
      if (!isLoaded) {
        setErrorMessage(
          language === "ta"
            ? "Razorpay பணம் செலுத்தும் முறையை ஏற்ற முடியவில்லை. தயவுசெய்து மீண்டும் முயற்சிக்கவும்."
            : "Could not load Razorpay payment gateway. Please check your internet connection."
        );
        setIsProcessing(false);
        return;
      }

      // Create Order
      const res = await fetch("/api/payments/create-order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          planId: requiredPlan,
          billingCycle: "monthly",
        }),
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
        description: `${data.planNameEn} Subscription (Monthly)`,
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
                planId: requiredPlan,
                billingCycle: "monthly",
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

      const razorpay = new window.Razorpay(options);
      razorpay.open();
    } catch (err: any) {
      setErrorMessage(err.message || "An unexpected error occurred.");
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg overflow-hidden rounded-2xl bg-white shadow-2xl border border-amber-200">
        {/* Decorative Header Banner */}
        <div className="relative bg-gradient-to-r from-[#153F6B] via-[#1E4E82] to-[#B4872B] p-6 text-white text-center">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1.5 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="mx-auto w-12 h-12 rounded-full bg-amber-400/20 border border-amber-300/40 flex items-center justify-center mb-3">
            <Crown className="w-6 h-6 text-amber-300 animate-pulse" />
          </div>
          <span className="inline-block px-3 py-0.5 rounded-full text-[11px] font-bold tracking-wide uppercase bg-amber-400 text-stone-900 mb-2">
            {language === "ta" ? "கட்டண சேவை" : "Paid Software Tool"}
          </span>
          <h3 className="text-xl font-bold leading-snug">
            {language === "ta" ? toolNameTa : toolNameEn}
          </h3>
          <p className="text-xs text-amber-100/90 mt-1">
            {language === "ta"
              ? "இக்கருவியைப் பயன்படுத்த சந்தா திட்டத்தை ஆக்டிவேட் செய்யவும்"
              : "Upgrade your subscription to unlock this professional tool"}
          </p>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5">
          {errorMessage && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs">
              {errorMessage}
            </div>
          )}

          <div className="rounded-xl bg-[#FAF2DE]/60 border border-[#B4872B]/30 p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[#8B6914] uppercase tracking-wider">
                {language === "ta" ? "பரிந்துரைக்கப்படும் திட்டம்" : "Recommended Plan"}
              </span>
              <span className="text-sm font-extrabold text-[#153F6B]">
                ₹{priceInr.toLocaleString()}/mo
              </span>
            </div>
            <h4 className="text-base font-bold text-[#183047]">
              {language === "ta" ? planTitleTa : planTitleEn}
            </h4>
            <ul className="text-xs text-[#52667E] space-y-1.5 pt-1">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>
                  {language === "ta"
                    ? "அளவற்ற துல்லிய கணிப்புகள் & சுவிஸ் எஃபிமெரிஸ் கணக்கீடுகள்"
                    : "Unlimited high-precision Swiss Ephemeris calculations"}
                </span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>
                  {language === "ta"
                    ? "உயர் ரக அச்சிடத்தக்க பிடிஎஃப் அறிக்கைகள்"
                    : "Publication-grade vector PDF reports & booklet printing"}
                </span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>
                  {language === "ta"
                    ? "வாடிக்கையாளர் மேலாண்மை (CRM) & உடனடி வாடிக்கையாளர் வாக்கு பலகை"
                    : "Astrologer CRM directory & instant client consultation tools"}
                </span>
              </li>
            </ul>
          </div>

          <div className="space-y-3 pt-1">
            <button
              onClick={handleQuickCheckout}
              disabled={isProcessing}
              className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-[#153F6B] to-[#1E4E82] hover:from-[#113255] hover:to-[#173F6B] text-white font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-70"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>
                    {language === "ta" ? "பணம் செலுத்தும் திரை திறக்கிறது..." : "Opening Checkout..."}
                  </span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 text-amber-300" />
                  <span>
                    {language === "ta"
                      ? `இப்போதே ₹${priceInr.toLocaleString()} செலுத்தி திறக்க (UPI / Card)`
                      : `Instant Unlock for ₹${priceInr.toLocaleString()} (UPI / Card)`}
                  </span>
                </>
              )}
            </button>

            <Link
              href="/pricing"
              onClick={onClose}
              className="w-full py-2.5 px-4 rounded-xl border border-[#D9DEE7] hover:border-[#153F6B] text-[#153F6B] font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors bg-white hover:bg-slate-50"
            >
              <span>{language === "ta" ? "அனைத்து கட்டண திட்டங்களையும் காண்க" : "Compare All Subscription Plans"}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Trust Footnote */}
          <div className="flex items-center justify-center gap-2 text-[11px] text-[#8190A6] pt-1">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>
              {language === "ta"
                ? "Razorpay மூலம் 256-பிட் பாதுகாப்பான கட்டணம் | உடனடி ஆக்டிவேஷன்"
                : "256-Bit SSL Secured by Razorpay | Instant Automated Activation"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
