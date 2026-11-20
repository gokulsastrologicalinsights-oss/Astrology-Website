"use client";

import React from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { Lock, EyeOff, ShieldCheck, Database, Trash2, Mail, ArrowLeft } from "lucide-react";

export default function PrivacyPage() {
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
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-600">
              <Lock className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-serif font-bold text-[#0F172A]">
                {isTamil ? "தனியுரிமைக் கொள்கை" : "Privacy Policy"}
              </h1>
              <p className="text-xs text-[#64748B] mt-1">
                {isTamil
                  ? "கடைசியாக புதுப்பிக்கப்பட்டது: நவம்பர் 20, 2026 • இந்திய DPDP சட்டம் 2023 மற்றும் சர்வதேச தனியுரிமை நியதிகள்"
                  : "Last Updated: November 20, 2026 • Compliant with DPDP Act (India) & Global Privacy Standards"}
              </p>
            </div>
          </div>
        </div>

        {/* Commitment Banner */}
        <div className="p-5 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-950 space-y-2">
          <div className="flex items-center gap-2 font-semibold text-sm text-emerald-900">
            <EyeOff className="w-4 h-4 text-emerald-600" />
            <span>
              {isTamil ? "பூஜ்ஜிய தரவு விற்பனை • 100% ரகசியத்தன்மை உத்தரவாதம்" : "Zero Data Selling • 100% Confidentiality Guarantee"}
            </span>
          </div>
          <p className="text-xs leading-relaxed text-emerald-800/90">
            {isTamil
              ? "உங்கள் பிறப்பு விவரங்கள் (பிறந்த தேதி, நேரம், இடம்) மற்றும் ஜாதகக் குறிப்புகள் உங்களின் புனிதமான தனிப்பட்ட தகவல்களாகும். அவற்றை நாங்கள் ஒருபோதும் விளம்பர நிறுவனங்களுக்கோ அல்லது மூன்றாம் தரப்பினருக்கோ விற்பனை செய்வதில்லை."
              : "We recognize that birth charts, birth moments, and family horoscopes represent intimate personal data. Gokul's Astrological Insights does not sell, rent, monetize, or trade your personal or birth records to any third-party brokers, advertisers, or data aggregators."}
          </p>
        </div>

        {/* Section 1: Information Collected */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB]">
              <Database className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "1. நாங்கள் சேகரிக்கும் தகவல்கள்" : "1. Information We Collect"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <p>
              {isTamil
                ? "துல்லியமான வானியல் கணக்கீடுகளைச் செய்வதற்கு பின்வரும் குறைந்தபட்சத் தகவல்களை நாங்கள் சேகரிக்கிறோம்:"
                : "To execute mathematically exact planetary and astrological computations, we collect:"}
            </p>
            <ul className="list-disc pl-5 space-y-1 text-[#475569]">
              <li>
                <strong>{isTamil ? "பிறப்பு விவரங்கள்" : "Astronomical Input Data"}</strong>:{" "}
                {isTamil
                  ? "பெயர், பாலினம், பிறந்த தேதி, பிறந்த நேரம் மற்றும் பிறந்த ஊர்/புவியியல் ஆயத்தொலைவுகள் (அட்சரேகை, தீர்க்கரேகை)."
                  : "Name, gender, Date of Birth, Time of Birth, city/geographic coordinates (latitude and longitude)."}
              </li>
              <li>
                <strong>{isTamil ? "கணக்கு விவரங்கள்" : "Account Identity"}</strong>:{" "}
                {isTamil ? "மின்னஞ்சல் முகவரி, பயனர் பெயர் மற்றும் குறியாக்கம் செய்யப்பட்ட கடவுச்சொல்." : "Email address, username, and securely hashed passwords."}
              </li>
              <li>
                <strong>{isTamil ? "பரிவர்த்தனை பதிவுகள்" : "Commercial Transaction Logs"}</strong>:{" "}
                {isTamil
                  ? "பரிவர்த்தனை எண், வாங்கிய அறிக்கையின் வகை மற்றும் தேதி (உங்கள் வங்கி அட்டை எண்கள் எங்கள் சர்வரில் சேமிக்கப்படுவதில்லை; அவை பாதுகாப்பான கட்டண வாயில்களால் மட்டுமே கையாளப்படுகின்றன)."
                  : "Order timestamps, transaction reference IDs, and purchased PDF reports. We never store credit card or debit card credentials on our servers; payments are processed directly by certified PCI-DSS payment gateways."}
              </li>
            </ul>
          </div>
        </section>

        {/* Section 2: How We Use Your Data */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "2. தரவுகளை நாங்கள் எவ்வாறு பயன்படுத்துகிறோம்" : "2. How We Use Collected Data"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <p>
              {isTamil
                ? "சேகரிக்கப்படும் தகவல்கள் கீழ்க்கண்ட நோக்கங்களுக்கு மட்டுமே பயன்படுத்தப்படுகின்றன:"
                : "Your data is used strictly for technical and operational fulfillment:"}
            </p>
            <ul className="list-disc pl-5 space-y-1 text-[#475569]">
              <li>
                {isTamil
                  ? "வேத மற்றும் கே.பி முறைப்படி லக்னம், நவாம்சம், தசா புக்தி, அஷ்டகவர்க்கம் மற்றும் ஷட்பல கணிப்புகளை துல்லியமாகக் கணக்கிட."
                  : "Executing high-precision planetary longitudes, Placidus cusps, Vimshottari dasas, and Shadbala strengths via the native XALEN engine."}
              </li>
              <li>
                {isTamil
                  ? "நீங்கள் பதிவிறக்கம் செய்யக் கோரும் 9-பக்க பிடிஎஃப் ஜாதக அறிக்கைகளை வடிவமைத்து வழங்க."
                  : "Generating high-resolution 9-page and 6-page vector PDF reports with Tamil typography."}
              </li>
              <li>
                {isTamil
                  ? "உங்கள் சொந்த கணக்கு பெட்டகத்தில் (Vault) ஜாதகங்களை பத்திரமாகச் சேமித்து வைக்க."
                  : "Preserving your saved horoscopes and CRM client profiles with user-isolated Row-Level Security."}
              </li>
            </ul>
          </div>
        </section>

        {/* Section 3: Data Security and Encryption */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600">
              <Lock className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "3. தரவு பாதுகாப்பு & குறியாக்கம்" : "3. Technical Data Security & Encryption"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <p>
              {isTamil
                ? "அனைத்து இணையப் பரிமாற்றங்களும் TLS 1.3 / HTTPS மூலம் குறியாக்கம் (Encrypted in Transit) செய்யப்பட்டு அனுப்பப்படுகின்றன. தரவுத்தளத்தில் சேமிக்கப்படும் பதிவுகள் Supabase PostgreSQL மட்டத்திலான Row-Level Security (RLS) மூலம் தனிமைப்படுத்தப்பட்டுள்ளன. ஒரு பயனரின் ஜாதகத்தை மற்றொரு பயனரால் ஒருபோதும் பார்க்க முடியாது."
                : "All data transmission between your browser and our servers is encrypted using modern TLS 1.3 encryption (HTTPS). Persistent records in Supabase PostgreSQL are strictly isolated via Row-Level Security (RLS) policies requiring cryptographic user JWT tokens. No user can view or query another user's saved charts."}
            </p>
          </div>
        </section>

        {/* Section 4: User Rights (Deletion & Correction) */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600">
              <Trash2 className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "4. உங்கள் உரிமைகள் (தரவு நீக்கம் & திருத்தம்)" : "4. Your Data Rights & Deletion"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <p>
              {isTamil
                ? "உங்கள் கணக்கில் சேமிக்கப்பட்டுள்ள எந்தவொரு ஜாதகத்தையும் எந்த நேரத்திலும் நீங்கள் திருத்தவோ அல்லது நிரந்தரமாக நீக்கவோ உரிமை உண்டு. உங்கள் முழு பயனர் கணக்கையும் அதன் அனைத்து பதிவுகளையும் நிரந்தரமாக நீக்க விரும்பினால், எங்களின் ஆதரவு மின்னஞ்சலுக்கு கோரிக்கை அனுப்பலாம்."
                : "Under applicable data privacy regulations, you retain full rights to access, rectify, export, or permanently delete any saved birth profile or customer record stored in your dashboard. You may request total account erasure at any time."}
            </p>
          </div>
        </section>

        {/* Section 5: Grievance Officer */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600">
              <Mail className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "5. குறைதீர்க்கும் அதிகாரி & தொடர்புக்கு" : "5. Grievance Redressal Officer"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <p>
              {isTamil
                ? "இந்திய தகவல் தொழில்நுட்ப விதிகளின்படி நியமிக்கப்பட்ட குறைதீர்க்கும் அதிகாரியைத் தொடர்பு கொள்ள:"
                : "In accordance with the Information Technology Act (India) and DPDP guidelines, our Grievance Officer can be reached at:"}
            </p>
            <div className="bg-[#F8FAFC] p-4 rounded-xl border border-[#E2E8F0] space-y-1 font-mono text-[11px] text-[#334155]">
              <div><strong>Grievance & Data Protection Officer</strong>: Gokul's Astrological Insights</div>
              <div><strong>Official Email</strong>: privacy@gokulsastrology.com</div>
              <div><strong>Support Response Time</strong>: Within 48 hours</div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
