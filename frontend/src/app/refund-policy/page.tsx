"use client";

import React from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { RefreshCcw, CheckCircle, AlertCircle, Clock, CreditCard, ArrowLeft } from "lucide-react";

export default function RefundPolicyPage() {
  const { language } = useLanguage();
  const isTamil = language === "ta";

  return (
    <div className="min-h-screen bg-[#FDFBF7] text-[#1E293B] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Navigation & Header */}
        <div>
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-xs font-medium text-[#2563EB] hover:text-[#1D4ED8] mb-6 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            {isTamil ? "முகப்புப் பக்கத்திற்குத் திரும்பு" : "Return to Home"}
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-600">
              <RefreshCcw className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-serif font-bold text-[#0F172A]">
                {isTamil ? "பணத்தைத் திரும்பப்பெறுதல் & ரத்து செய்தல் கொள்கை" : "Refund & Cancellation Policy"}
              </h1>
              <p className="text-xs text-[#64748B] mt-1">
                {isTamil
                  ? "கடைசியாக புதுப்பிக்கப்பட்டது: நவம்பர் 20, 2026 • வணிக கட்டண விதிமுறைகள்"
                  : "Last Updated: November 20, 2026 • Commercial Payment & Consumer Policy"}
              </p>
            </div>
          </div>
        </div>

        {/* Digital Products Notice Banner */}
        <div className="p-5 rounded-2xl bg-purple-50 border border-purple-200 text-purple-950 space-y-2">
          <div className="flex items-center gap-2 font-semibold text-sm text-purple-900">
            <AlertCircle className="w-4 h-4 text-purple-600" />
            <span>
              {isTamil ? "தனிப்பயனாக்கப்பட்ட டிஜிட்டல் அறிக்கைகளின் தன்மை" : "Nature of Personalized Digital Products"}
            </span>
          </div>
          <p className="text-xs leading-relaxed text-purple-800/90">
            {isTamil
              ? "கோகுலின் ஜோதிட நுண்ணறிவுகள் தளத்தில் வழங்கப்படும் ஜாதக கணிப்புகள் மற்றும் 9-பக்க பிடிஎஃப் புத்தகங்கள் நீங்கள் உள்ளீடு செய்யும் பிறந்த தேதி மற்றும் நேரத்தின் அடிப்படையில் உடனடியாக பிரத்தியேகமாக உருவாக்கப்படும் டிஜிட்டல் சேவைகளாகும். எனவே, ஒருமுறை வெற்றிகரமாக உருவாக்கப்பட்ட அறிக்கைகளை திரும்பப் பெற முடியாது."
              : "Horoscope computations, KP sub-lord tables, and 9-page vector PDF reports generated on Gokul's Astrological Insights are customized, instantaneous digital products tailored specifically to the unique birth coordinates supplied. Due to the irrevocable digital nature of these goods, standard return procedures for physical items do not apply."}
          </p>
        </div>

        {/* Section 1: When Refunds ARE Granted */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600">
              <CheckCircle className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "1. பணம் திரும்ப வழங்கப்படும் சந்தர்ப்பங்கள்" : "1. When Refunds Are Issued"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <p>
              {isTamil
                ? "பின்வரும் நியாயமான காரணங்களுக்கு 100% முழுத் தொகையும் எந்தவித பிடித்தமுமின்றி திரும்ப வழங்கப்படும்:"
                : "A full 100% refund will be granted without penalty under the following verified conditions:"}
            </p>
            <ul className="list-disc pl-5 space-y-2 text-[#475569]">
              <li>
                <strong>{isTamil ? "இரட்டிப்புக் கட்டணம் (Duplicate Charge)" : "Duplicate Billing"}</strong>:{" "}
                {isTamil
                  ? "தொழில்நுட்ப கோளாறு அல்லது நெட்வொர்க் பிரச்சனையால் ஒரே அறிக்கைக்கு உங்கள் வங்கிக் கணக்கிலிருந்து இரண்டு முறை பணம் கழிக்கப்பட்டால், கூடுதல் கட்டணம் உடனடியாக திருப்பித் தரப்படும்."
                  : "If a technical glitch or network latency results in multiple charges for the same single report or transaction, all duplicate charges will be refunded automatically."}
              </li>
              <li>
                <strong>{isTamil ? "தொழில்நுட்பப் பிழை (Technical Failure)" : "Service Generation Failure"}</strong>:{" "}
                {isTamil
                  ? "பணம் செலுத்தப்பட்ட பிறகும், சர்வர் கோளாறு காரணமாக உங்கள் பிடிஎஃப் அறிக்கை உருவாக்கப்படாமல், எங்கள் தொழில்நுட்ப ஆதரவுக் குழுவால் 48 மணி நேரத்திற்குள் அதை வழங்க முடியாவிட்டால் முழுப் பணமும் திருப்பித் தரப்படும்."
                  : "If payment succeeds but our backend fails to generate or deliver your purchased PDF report, and our engineering desk is unable to resolve and deliver the report within 48 hours."}
              </li>
            </ul>
          </div>
        </section>

        {/* Section 2: When Refunds Are NOT Granted */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600">
              <AlertCircle className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "2. பணம் திரும்ப வழங்கப்படாத சந்தர்ப்பங்கள்" : "2. Non-Refundable Circumstances"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <ul className="list-disc pl-5 space-y-2 text-[#475569]">
              <li>
                <strong>{isTamil ? "ஜோதிடப் பலன்களில் திருப்தியின்மை" : "Subjective Disagreement with Predictions"}</strong>:{" "}
                {isTamil
                  ? "ஜோதிடப் பலன்கள் பாரம்பரிய சாஸ்திர விதிகளின் அடிப்படையிலான வழிகாட்டல் மட்டுமே. எதிர்காலப் பலன்கள் உங்கள் விருப்பப்படி அமையவில்லை என்பதற்காக கட்டணத்தைத் திரும்பப் பெற முடியாது."
                  : "Astrological predictions, dasa evaluations, and compatibility scores are subjective guidance based on traditional treatises. Disappointment with an astrological outlook does not qualify for a refund."}
              </li>
              <li>
                <strong>{isTamil ? "தவறான பிறப்பு விவரங்களை உள்ளிடுதல்" : "User Input Inaccuracies"}</strong>:{" "}
                {isTamil
                  ? "பயனர் தவறான பிறந்த நேரம், தேதி அல்லது ஊரை உள்ளீடு செய்து அறிக்கை உருவாக்கிய பிறகு பணத்தைத் திரும்பப் பெற முடியாது (இருப்பினும் எங்கள் தளத்தில் உங்கள் கணக்கிலிருந்து விவரங்களைத் திருத்தி மீண்டும் கணக்கிட வசதி உண்டு)."
                  : "If you entered an incorrect birth date, wrong birth time, or incorrect city coordinates, refunds cannot be issued. Users can edit saved profiles and re-run calculations."}
              </li>
              <li>
                <strong>{isTamil ? "பிடிஎஃப் பதிவிறக்கம் செய்த பின் மனமாற்றம்" : "Post-Download Change of Mind"}</strong>:{" "}
                {isTamil
                  ? "முழு அறிக்கையையும் பதிவிறக்கம் செய்து பார்த்த பின் மனமாற்றம் காரணமாக பணத்தைத் திரும்பப் பெற முடியாது."
                  : "Change of mind after the report file has been downloaded or viewed."}
              </li>
            </ul>
          </div>
        </section>

        {/* Section 3: Subscription Cancellations */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB]">
              <Clock className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "3. சந்தா ரத்து செய்தல் (Subscriptions)" : "3. Recurring Subscription Cancellation"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <p>
              {isTamil
                ? "தொழில்முறை ஜோதிடர்களுக்கான மாதாந்திர அல்லது வருடாந்திர சந்தா திட்டங்களை நீங்கள் எந்த நேரத்திலும் உங்கள் டாஷ்போர்டு வழியாக ஒரே கிளிக்கில் ரத்து செய்யலாம். ரத்து செய்த பிறகும், நடப்பு கட்டணக் காலம் முடியும் வரை சந்தாவின் அனைத்து பலன்களையும் நீங்கள் தொடர்ந்து பயன்படுத்தலாம்."
                : "Professional tier subscribers may cancel their monthly or annual recurring plans at any time directly through their account settings. Upon cancellation, access remains active until the end of the current billing cycle without any further automated renewals."}
            </p>
          </div>
        </section>

        {/* Section 4: Refund Processing Timelines */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600">
              <CreditCard className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "4. பணம் திரும்ப வரும் கால அளவு" : "4. Refund Processing Timeline"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <p>
              {isTamil
                ? "அங்கீகரிக்கப்பட்ட பணம் திரும்பப் பெறுதல் கோரிக்கைகள் பரிசீலிக்கப்பட்டு, உங்கள் அசல் கட்டண முறைக்கே (வங்கி கணக்கு, UPI, அல்லது கிரெடிட் கார்டு) 5 முதல் 7 வேலை நாட்களுக்குள் (5-7 Business Days) வரவு வைக்கப்படும்."
                : "Approved refunds are submitted immediately to our payment gateway partners (Razorpay / Stripe) and are credited back to the customer's original payment method (Bank Account, UPI, or Card) within 5 to 7 business days, depending on banking clearing cycles."}
            </p>
            <div className="bg-[#F8FAFC] p-4 rounded-xl border border-[#E2E8F0] text-[11px] space-y-1">
              <div><strong>Billing Desk</strong>: billing@gokulsastrology.com</div>
              <div><strong>Support Working Hours</strong>: Monday – Saturday, 9:00 AM – 6:00 PM IST</div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
