"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { useLanguage } from "@/lib/i18n";
import { ShieldCheck } from "lucide-react";

export function Footer() {
  const pathname = usePathname();
  const { language, t } = useLanguage();
  const isLoginPage = pathname === "/login" || pathname === "/forgot-password" || pathname === "/register";

  if (pathname === "/login") {
    return null;
  }

  return (
    <footer className="w-full border-t border-[#DDE5F0] bg-white text-[#52667E] mt-auto print:hidden">
      <div className="w-full px-4 sm:px-6 lg:px-8 2xl:px-10 py-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Brand & Mission */}
          <div className="lg:col-span-2 space-y-3">
            <div className="flex items-center gap-2.5">
              <div className="relative w-8 h-8 rounded-lg overflow-hidden border border-[#B8862B]/30 shadow-xs bg-[#090d2e] shrink-0">
                <Image
                  src="/logo.png"
                  alt="Gokul's Astrological Insights Logo"
                  width={32}
                  height={32}
                  className="w-full h-full object-cover"
                />
              </div>
              <span className="font-serif text-lg font-bold text-[#102A4C]">
                {t.brandName}
              </span>
            </div>
            <p className="text-xs text-[#52667E] leading-relaxed max-w-md">
              {t.heroSubtitle}
            </p>
            <div className="flex items-center gap-2 text-[11px] text-[#3478F6] font-medium pt-1">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>{t.footerEngineInfo}</span>
            </div>
          </div>

          {/* Quick Links */}
          {!isLoginPage ? (
            <div>
              <h5 className="text-xs font-bold uppercase tracking-wider text-[#102A4C] mb-3">
                {language === "ta" ? "முக்கிய வழிகாட்டல்" : "Application"}
              </h5>
              <ul className="space-y-2 text-xs">
                <li>
                  <Link href="/" className="hover:text-[#3478F6] transition-colors">
                    {t.navHome || "Home"}
                  </Link>
                </li>
                <li>
                  <Link href="/dashboard" className="hover:text-[#3478F6] transition-colors">
                    {t.navDashboard}
                  </Link>
                </li>
                <li>
                  <Link href="/tools" className="hover:text-[#3478F6] transition-colors">
                    {t.navTools || "Astrology Tools"}
                  </Link>
                </li>
                <li>
                  <Link href="/pricing" className="hover:text-[#3478F6] text-[#B8862B] font-semibold transition-colors">
                    {language === "ta" ? "கட்டண திட்டங்கள் (Pricing)" : "Plans & Pricing"}
                  </Link>
                </li>
                <li>
                  <Link href="/tools/horoscope" className="hover:text-[#3478F6] transition-colors">
                    Horoscope / KP System
                  </Link>
                </li>
                <li>
                  <Link href="/tools/numerology" className="hover:text-[#3478F6] transition-colors">
                    Numerology
                  </Link>
                </li>
              </ul>
            </div>
          ) : (
            <div>
              <h5 className="text-xs font-bold uppercase tracking-wider text-[#0F172A] mb-3">
                {language === "ta" ? "அணுகல் பாதுகாப்பு" : "Access Security"}
              </h5>
              <p className="text-xs text-[#64748B] leading-relaxed">
                {language === "ta"
                  ? "அங்கீகரிக்கப்பட்ட பயனர்களுக்கு மட்டுமே அனுமதி. உள்நுழைவு அவசியம்."
                  : "Authenticated access only. Sign in required to enter the application portal."}
              </p>
            </div>
          )}

          {/* Systems Supported */}
          <div>
            <h5 className="text-xs font-bold uppercase tracking-wider text-[#0F172A] mb-3">
              {language === "ta" ? "கணித முறைகள்" : "Supported Canons"}
            </h5>
            <ul className="space-y-2 text-xs text-[#64748B]">
              <li>{language === "ta" ? "சித்ரபக்ஷ லஹரி அயனாம்சம்" : "Lahiri (Chitrapaksha) Sidereal"}</li>
              <li>{language === "ta" ? "கே.பி முறை (249 உப அதிபதிகள்)" : "KP Sub-Lord System (249 Sub-Lords)"}</li>
              <li>{language === "ta" ? "விம்சோத்தரி தசை (365.25 நாள்)" : "Vimshottari Dasa (365.25d)"}</li>
              <li>{language === "ta" ? "தென்/வடஇந்திய கட்ட அமைப்புகள்" : "South & North Indian Charts"}</li>
            </ul>
          </div>

          {/* Legal & Policies (Crucial for Commercial Compliance & Payment Gateways) */}
          <div>
            <h5 className="text-xs font-bold uppercase tracking-wider text-[#0F172A] mb-3">
              {language === "ta" ? "சட்டம் & கொள்கைகள்" : "Legal & Compliance"}
            </h5>
            <ul className="space-y-2 text-xs text-[#64748B]">
              <li>
                <Link href="/disclaimer" className="hover:text-[#3478F6] transition-colors">
                  {language === "ta" ? "பொறுப்புத் துறப்பு (Disclaimer)" : "Methodology Disclaimer"}
                </Link>
              </li>
              <li>
                <Link href="/terms" className="hover:text-[#3478F6] transition-colors">
                  {language === "ta" ? "விதிமுறைகள் (Terms of Service)" : "Terms of Service"}
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="hover:text-[#3478F6] transition-colors">
                  {language === "ta" ? "தனியுரிமை (Privacy Policy)" : "Privacy Policy (DPDP/GDPR)"}
                </Link>
              </li>
              <li>
                <Link href="/refund-policy" className="hover:text-[#3478F6] transition-colors">
                  {language === "ta" ? "பணத் திரும்பப் பெறல் (Refund Policy)" : "Refund & Cancellation"}
                </Link>
              </li>
              <li>
                <Link href="/contact" className="hover:text-[#3478F6] transition-colors font-medium text-[#2563EB]">
                  {language === "ta" ? "தொடர்பு & உதவி (Contact Us)" : "Contact & Support Desk"}
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Methodology & Legal Disclaimer Notice */}
        <div className="mt-8 pt-6 border-t border-[#E8DEC8]/80 text-[11px] text-[#64748B] space-y-2">
          <p className="leading-relaxed">
            <strong className="text-[#0F172A]">
              {language === "ta" ? "முக்கிய அறிவிப்பு" : "Methodology Disclaimer"}:
            </strong>{" "}
            {t.footerDisclaimer}
          </p>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pt-2 text-[#94A3B8]">
            <div>{t.footerCopyright} • Geocoding © OpenStreetMap contributors</div>
            <div className="font-mono text-[10px]">Official Astrological Calculations • Mathematical Precision</div>
          </div>
        </div>
      </div>
    </footer>
  );
}
