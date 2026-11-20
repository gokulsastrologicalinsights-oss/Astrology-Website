"use client";

import React from "react";
import Link from "next/link";
import { useLanguage } from "@/lib/i18n";
import { FileText, CheckCircle2, ShieldAlert, Award, Ban, Globe2, ArrowLeft } from "lucide-react";

export default function TermsPage() {
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
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-[#2563EB]">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-serif font-bold text-[#0F172A]">
                {isTamil ? "பயன்பாட்டு விதிமுறைகள் & நிபந்தனைகள்" : "Terms of Service"}
              </h1>
              <p className="text-xs text-[#64748B] mt-1">
                {isTamil
                  ? "கடைசியாக புதுப்பிக்கப்பட்டது: நவம்பர் 20, 2026 • பயன்பாட்டு வழிகாட்டி"
                  : "Last Updated: November 20, 2026 • Standard User Agreement"}
              </p>
            </div>
          </div>
        </div>

        {/* Section 1: Agreement to Terms */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "1. விதிமுறைகளை ஒப்புக்கொள்ளுதல்" : "1. Acceptance of Terms"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <p>
              {isTamil
                ? "கோகுலின் ஜோதிட நுண்ணறிவுகள் (Gokul's Astrological Insights - GAI) வலைத்தளத்தை அணுகுவதன் மூலமோ அல்லது பயன்படுத்துவதன் மூலமோ, நீங்கள் இந்த விதிமுறைகளையும் எங்களின் தனியுரிமைக் கொள்கையையும் முழுமையாக ஏற்றுக்கொள்கிறீர்கள். இந்த விதிமுறைகளில் உடன்பாடு இல்லாவிட்டால், இத்தளத்தைப் பயன்படுத்துவதைத் தவிர்க்கவும்."
                : "By accessing, registering with, or utilizing Gokul's Astrological Insights (GAI), you legally agree to be bound by these Terms of Service, our Privacy Policy, and our Methodology Disclaimer. If you do not agree to all terms, you must discontinue use immediately."}
            </p>
          </div>
        </section>

        {/* Section 2: Account Registration and Security */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-[#2563EB]">
              <ShieldAlert className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "2. பயனர் கணக்கு மற்றும் கடவுச்சொல் பாதுகாப்பு" : "2. User Accounts & Responsibilities"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <p>
              {isTamil
                ? "சேமிக்கப்பட்ட ஜாதகங்கள் மற்றும் நிர்வாக அம்சங்களை அணுக பயனர் கணக்கு உருவாக்க வேண்டும். உங்கள் கணக்கின் கடவுச்சொல் மற்றும் அமர்வுகளின் பாதுகாப்பிற்கு நீங்களே முழுப் பொறுப்பாவீர்கள். உங்கள் கணக்கின் மூலம் நடக்கும் அனைத்து செயல்பாடுகளுக்கும் நீங்களே பொறுப்பாவீர்கள்."
                : "To access saved horoscope archives, CRM client vaults, and personalized calculations, you must maintain an authenticated account. You are solely responsible for maintaining the confidentiality of your credentials and for all activities conducted under your account."}
            </p>
          </div>
        </section>

        {/* Section 3: Intellectual Property & Commercial License of Reports */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-600">
              <Award className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "3. அறிவுசார் சொத்துரிமை & வணிக பயன்பாட்டு உரிமைகள்" : "3. Intellectual Property & Commercial License for Reports"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <p>
              {isTamil
                ? "இத்தளத்தின் மென்பொருள் கட்டமைப்பு, பயனர் இடைமுகம், வரைகலை வடிவமைப்பு மற்றும் பிரத்தியேக அல்காரிதம்கள் கோகுலின் ஜோதிட நுண்ணறிவுகளுக்குச் சொந்தமான அறிவுசார் சொத்துக்களாகும்."
                : "All website interfaces, styling, vector rendering designs, custom analytical algorithms, and branding assets remain the exclusive intellectual property of Gokul's Astrological Insights."}
            </p>
            <p className="font-semibold text-emerald-800 bg-emerald-50 p-3 rounded-lg border border-emerald-200">
              {isTamil
                ? "✅ தொழில்முறை ஜோதிடர்களுக்கான வணிக உரிமை: இத்தளத்திலிருந்து நீங்கள் பதிவிறக்கம் செய்யும் 9-பக்க ஜாதக புத்தகங்கள் (PDF Reports), திருமணப் பொருத்த அறிக்கைகள் மற்றும் கே.பி அட்டவணைகளை நீங்கள் உங்கள் வாடிக்கையாளர்களுக்கு வழங்குவதற்கோ அல்லது வணிக ரீதியாக பயன்படுத்துவதற்கோ முழு உரிமை உண்டு."
                : "✅ Commercial Rights for Practitioners: Practicing astrologers, consultants, and clients possess full rights to print, brand, distribute, and commercially share with their clients any 9-page PDF Horoscope Reports, KP Charts, or Compatibility Booklets generated through their authorized accounts."}
            </p>
          </div>
        </section>

        {/* Section 4: Prohibited Uses */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-600">
              <Ban className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "4. தடைசெய்யப்பட்ட பயன்பாடுகள்" : "4. Prohibited Conduct"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <p>
              {isTamil ? "பயனர்கள் பின்வரும் செயல்களில் ஈடுபடக்கூடாது:" : "You strictly agree not to engage in:"}
            </p>
            <ul className="list-disc pl-5 space-y-1 text-[#475569]">
              <li>
                {isTamil
                  ? "தானியங்கி ஸ்கிராப்பர்கள் (Scrapers/Bots) மூலம் தளத்தின் தரவுகளை மொத்தமாகத் திருடுதல் அல்லது சேவையகத்தை முடக்குதல் (DDoS)."
                  : "Automated scraping, bulk harvesting of proprietary calculation tables, or launching Denial-of-Service attacks."}
              </li>
              <li>
                {isTamil
                  ? "அனுமதியின்றி பிற பயனர்களின் ஜாதகங்களை அல்லது தனிப்பட்ட தகவல்களை அணுக முயற்சித்தல்."
                  : "Attempting to bypass database Row-Level Security (RLS) to access other users' saved charts."}
              </li>
              <li>
                {isTamil
                  ? "தளத்தின் ஏபிஐ (API) அல்லது அல்காரிதம்களை சட்டவிரோதமாக மீள்வடிவமைத்தல் (Reverse Engineering)."
                  : "Decompiling or reverse-engineering proprietary backend calculation services."}
              </li>
            </ul>
          </div>
        </section>

        {/* Section 5: Governing Law & Jurisdiction */}
        <section className="bg-white rounded-2xl p-6 sm:p-8 border border-[#E2E8F0] shadow-xs space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600">
              <Globe2 className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-bold text-[#0F172A]">
              {isTamil ? "5. ஆளுகை சட்டம் & சட்ட வரம்பு" : "5. Governing Law & Jurisdiction"}
            </h2>
          </div>
          <div className="text-xs text-[#475569] leading-relaxed space-y-3">
            <p>
              {isTamil
                ? "இந்த விதிமுறைகள் இந்தியக் குடியரசின் சட்டங்களுக்கு உட்பட்டு நிர்வகிக்கப்படுகின்றன. எழும் எந்தவொரு சட்டரீதியான சர்ச்சைகளும் சென்னை, தமிழ்நாடு, இந்தியா ஆகியவற்றின் அதிகார வரம்பிற்கு உட்பட்ட நீதிமன்றங்களால் மட்டுமே விசாரிக்கப்படும்."
                : "These Terms of Service are governed by and construed in accordance with the laws of the Republic of India. Any disputes arising in connection with these terms shall be subject to the exclusive jurisdiction of the competent courts in Chennai, Tamil Nadu, India."}
            </p>
          </div>
        </section>

        {/* Closing Note */}
        <div className="text-center pt-4 text-xs text-[#64748B]">
          <p>
            {isTamil
              ? "விதிமுறைகள் குறித்த சந்தேகங்களுக்கு support@gokulsastrology.com என்ற மின்னஞ்சல் மூலம் எங்களைத் தொடர்பு கொள்ளவும்."
              : "For questions regarding our terms, contact our legal desk at support@gokulsastrology.com."}
          </p>
        </div>
      </div>
    </div>
  );
}
